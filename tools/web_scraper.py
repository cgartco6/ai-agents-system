import asyncio
import aiohttp
from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup
import json
import re
from urllib.parse import urljoin, urlparse
import time
import logging

class WebScraper:
    """Advanced web scraping tool with AI-powered data extraction"""
    
    def __init__(self, max_concurrent_requests: int = 5, request_delay: float = 1.0):
        self.max_concurrent_requests = max_concurrent_requests
        self.request_delay = request_delay
        self.session = None
        self.rate_limiter = asyncio.Semaphore(max_concurrent_requests)
        self.logger = self._setup_logging()
        
    def _setup_logging(self):
        logger = logging.getLogger("WebScraper")
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        return logger

    async def __aenter__(self):
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def initialize(self):
        """Initialize the web scraper"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        )

    async def close(self):
        """Close the web scraper"""
        if self.session:
            await self.session.close()

    async def scrape_url(self, url: str, selectors: Dict[str, str] = None, 
                        extraction_rules: Dict[str, Any] = None) -> Dict[str, Any]:
        """Scrape data from a single URL with advanced extraction"""
        async with self.rate_limiter:
            try:
                await asyncio.sleep(self.request_delay)  # Rate limiting
                
                self.logger.info(f"Scraping URL: {url}")
                
                async with self.session.get(url) as response:
                    if response.status != 200:
                        return {
                            'status': 'error',
                            'error': f"HTTP {response.status}",
                            'url': url
                        }
                    
                    html = await response.text()
                    extracted_data = await self._extract_data(html, selectors, extraction_rules, url)
                    
                    # Analyze content type and structure
                    content_analysis = await self._analyze_content(html, url)
                    
                    return {
                        'status': 'success',
                        'url': url,
                        'data': extracted_data,
                        'content_analysis': content_analysis,
                        'content_length': len(html),
                        'content_type': response.headers.get('content-type', 'unknown'),
                        'response_time': 'measured'  # Would be actual measurement
                    }
                    
            except Exception as e:
                self.logger.error(f"Error scraping {url}: {str(e)}")
                return {
                    'status': 'error',
                    'error': str(e),
                    'url': url
                }

    async def scrape_multiple_urls(self, urls: List[str], 
                                 selectors: Dict[str, str] = None,
                                 extraction_rules: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Scrape data from multiple URLs concurrently"""
        tasks = [self.scrape_url(url, selectors, extraction_rules) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                processed_results.append({
                    'status': 'error',
                    'error': str(result)
                })
            else:
                processed_results.append(result)
        
        self.logger.info(f"Completed scraping {len(urls)} URLs")
        return processed_results

    async def scrape_with_pagination(self, base_url: str, 
                                   page_param: str = 'page',
                                   max_pages: int = 10,
                                   selectors: Dict[str, str] = None,
                                   extraction_rules: Dict[str, Any] = None) -> Dict[str, Any]:
        """Scrape data with pagination support"""
        all_data = []
        successful_pages = 0
        
        for page in range(1, max_pages + 1):
            # Construct page URL
            if '?' in base_url:
                page_url = f"{base_url}&{page_param}={page}"
            else:
                page_url = f"{base_url}?{page_param}={page}"
            
            result = await self.scrape_url(page_url, selectors, extraction_rules)
            
            if result['status'] == 'success' and result['data']:
                all_data.append({
                    'page': page,
                    'url': page_url,
                    'data': result['data'],
                    'content_analysis': result['content_analysis']
                })
                successful_pages += 1
                self.logger.info(f"Successfully scraped page {page}")
            else:
                self.logger.info(f"No data found on page {page}, stopping pagination")
                break
            
            # Be respectful to the server
            await asyncio.sleep(self.request_delay * 2)
        
        return {
            'status': 'success',
            'base_url': base_url,
            'total_pages_scraped': successful_pages,
            'total_data_points': sum(len(page_data['data']) for page_data in all_data),
            'pages': all_data
        }

    async def scrape_dynamic_content(self, url: str, wait_time: int = 5) -> Dict[str, Any]:
        """Scrape dynamic content (requires JavaScript execution)"""
        # Note: This is a placeholder for dynamic scraping
        # In production, this would use Selenium or Playwright
        self.logger.warning("Dynamic scraping requires additional setup with Selenium/Playwright")
        
        return {
            'status': 'error',
            'error': 'Dynamic content scraping requires Selenium/Playwright integration',
            'url': url,
            'suggestion': 'Implement with selenium or playwright for JavaScript-rendered content'
        }

    async def _extract_data(self, html: str, selectors: Dict[str, str], 
                          extraction_rules: Dict[str, Any], base_url: str) -> Dict[str, Any]:
        """Extract data from HTML using CSS selectors and AI-powered rules"""
        soup = BeautifulSoup(html, 'html.parser')
        extracted = {}

        if not selectors and not extraction_rules:
            # Default extraction if no specific rules provided
            extracted = await self._extract_common_patterns(soup, base_url)
        else:
            # Use provided selectors
            if selectors:
                for key, selector in selectors.items():
                    if selector.startswith('@'):
                        # Attribute extraction
                        attr_name = selector[1:]
                        elements = soup.select('[{}]'.format(attr_name))
                        extracted[key] = [element.get(attr_name) for element in elements]
                    else:
                        # Content extraction
                        elements = soup.select(selector)
                        if key.endswith('_text'):
                            extracted[key] = [element.get_text(strip=True) for element in elements]
                        elif key.endswith('_html'):
                            extracted[key] = [str(element) for element in elements]
                        else:
                            # Default to text
                            extracted[key] = [element.get_text(strip=True) for element in elements]

            # Apply AI-powered extraction rules if provided
            if extraction_rules:
                ai_extracted = await self._apply_ai_extraction_rules(soup, extraction_rules, base_url)
                extracted.update(ai_extracted)

        return extracted

    async def _extract_common_patterns(self, soup: BeautifulSoup, base_url: str) -> Dict[str, Any]:
        """Extract common data patterns from web pages"""
        patterns = {
            'title': self._safe_extract(soup, 'title'),
            'meta_description': self._extract_meta_description(soup),
            'headings': self._extract_headings(soup),
            'paragraphs': self._extract_paragraphs(soup),
            'links': self._extract_links(soup, base_url),
            'images': self._extract_images(soup, base_url),
            'tables': self._extract_tables(soup),
            'lists': self._extract_lists(soup),
            'contact_info': await self._extract_contact_info(soup),
            'social_links': self._extract_social_links(soup, base_url)
        }
        
        return patterns

    async def _apply_ai_extraction_rules(self, soup: BeautifulSoup, rules: Dict[str, Any], base_url: str) -> Dict[str, Any]:
        """Apply AI-powered extraction rules"""
        extracted = {}
        
        for rule_name, rule_config in rules.items():
            if rule_config.get('type') == 'pattern_based':
                extracted[rule_name] = await self._extract_with_patterns(soup, rule_config)
            elif rule_config.get('type') == 'semantic':
                extracted[rule_name] = await self._extract_semantic_content(soup, rule_config)
            elif rule_config.get('type') == 'structured_data':
                extracted[rule_name] = await self._extract_structured_data(soup, rule_config)
        
        return extracted

    async def _extract_with_patterns(self, soup: BeautifulSoup, rule_config: Dict[str, Any]) -> List[str]:
        """Extract data using pattern matching"""
        patterns = rule_config.get('patterns', [])
        results = []
        
        for pattern in patterns:
            if pattern['method'] == 'regex':
                text = soup.get_text()
                matches = re.findall(pattern['pattern'], text, re.IGNORECASE)
                results.extend(matches)
            elif pattern['method'] == 'css_selector':
                elements = soup.select(pattern['selector'])
                for element in elements:
                    if pattern.get('attribute'):
                        results.append(element.get(pattern['attribute']))
                    else:
                        results.append(element.get_text(strip=True))
        
        return list(set(results))  # Remove duplicates

    async def _extract_semantic_content(self, soup: BeautifulSoup, rule_config: Dict[str, Any]) -> Dict[str, Any]:
        """Extract semantic content using AI analysis"""
        # This would integrate with AI models in production
        text_content = soup.get_text()
        
        # Simplified semantic extraction
        semantic_data = {
            'topics': await self._extract_topics(text_content),
            'sentiment': await self._analyze_sentiment(text_content),
            'key_entities': await self._extract_entities(text_content),
            'summary': await self._generate_summary(text_content)
        }
        
        return semantic_data

    async def _extract_structured_data(self, soup: BeautifulSoup, rule_config: Dict[str, Any]) -> Dict[str, Any]:
        """Extract structured data (JSON-LD, Microdata, etc.)"""
        structured_data = {
            'json_ld': self._extract_json_ld(soup),
            'microdata': self._extract_microdata(soup),
            'opengraph': self._extract_opengraph(soup),
            'twitter_cards': self._extract_twitter_cards(soup)
        }
        
        return structured_data

    def _extract_json_ld(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract JSON-LD structured data"""
        json_ld_data = []
        scripts = soup.find_all('script', type='application/ld+json')
        
        for script in scripts:
            try:
                data = json.loads(script.string)
                json_ld_data.append(data)
            except:
                continue
        
        return json_ld_data

    def _extract_microdata(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract Microdata"""
        # Simplified microdata extraction
        microdata = []
        items = soup.find_all(itemscope=True)
        
        for item in items:
            item_data = {}
            properties = item.find_all(itemprop=True)
            
            for prop in properties:
                prop_name = prop.get('itemprop')
                if prop.get('content'):
                    prop_value = prop.get('content')
                else:
                    prop_value = prop.get_text(strip=True)
                
                item_data[prop_name] = prop_value
            
            if item_data:
                microdata.append(item_data)
        
        return microdata

    def _extract_opengraph(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract Open Graph metadata"""
        og_data = {}
        meta_tags = soup.find_all('meta', attrs={'property': re.compile(r'^og:')})
        
        for tag in meta_tags:
            property_name = tag.get('property', '').replace('og:', '')
            content = tag.get('content', '')
            og_data[property_name] = content
        
        return og_data

    def _extract_twitter_cards(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract Twitter Card metadata"""
        twitter_data = {}
        meta_tags = soup.find_all('meta', attrs={'name': re.compile(r'^twitter:')})
        
        for tag in meta_tags:
            property_name = tag.get('name', '').replace('twitter:', '')
            content = tag.get('content', '')
            twitter_data[property_name] = content
        
        return twitter_data

    async def _analyze_content(self, html: str, url: str) -> Dict[str, Any]:
        """Analyze content structure and quality"""
        soup = BeautifulSoup(html, 'html.parser')
        
        return {
            'word_count': len(soup.get_text().split()),
            'heading_structure': self._analyze_heading_structure(soup),
            'link_analysis': self._analyze_links(soup, url),
            'image_analysis': self._analyze_images(soup),
            'readability_score': await self._calculate_readability(soup),
            'content_categories': await self._categorize_content(soup),
            'language': await self._detect_language(soup)
        }

    def _analyze_heading_structure(self, soup: BeautifulSoup) -> Dict[str, int]:
        """Analyze heading structure"""
        headings = {'h1': 0, 'h2': 0, 'h3': 0, 'h4': 0, 'h5': 0, 'h6': 0}
        
        for level in headings.keys():
            headings[level] = len(soup.find_all(level))
        
        return headings

    def _analyze_links(self, soup: BeautifulSoup, base_url: str) -> Dict[str, Any]:
        """Analyze link structure"""
        links = soup.find_all('a', href=True)
        internal_links = []
        external_links = []
        
        for link in links:
            href = link['href']
            full_url = urljoin(base_url, href)
            
            if urlparse(full_url).netloc == urlparse(base_url).netloc:
                internal_links.append({
                    'text': link.get_text(strip=True),
                    'url': full_url
                })
            else:
                external_links.append({
                    'text': link.get_text(strip=True),
                    'url': full_url
                })
        
        return {
            'total_links': len(links),
            'internal_links': len(internal_links),
            'external_links': len(external_links),
            'internal_link_samples': internal_links[:10],  # Sample
            'external_link_samples': external_links[:10]   # Sample
        }

    def _analyze_images(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze images on the page"""
        images = soup.find_all('img')
        image_data = []
        
        for img in images:
            image_data.append({
                'src': img.get('src', ''),
                'alt': img.get('alt', ''),
                'width': img.get('width', ''),
                'height': img.get('height', '')
            })
        
        return {
            'total_images': len(images),
            'images_with_alt': len([img for img in images if img.get('alt')]),
            'image_samples': image_data[:10]
        }

    async def _calculate_readability(self, soup: BeautifulSoup) -> float:
        """Calculate readability score (simplified)"""
        text = soup.get_text()
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        
        if len(words) == 0 or len(sentences) == 0:
            return 0.0
        
        avg_sentence_length = len(words) / len(sentences)
        avg_word_length = sum(len(word) for word in words) / len(words)
        
        # Simplified readability formula
        readability = max(0, 100 - (avg_sentence_length + avg_word_length))
        return min(100, readability)

    async def _categorize_content(self, soup: BeautifulSoup) -> List[str]:
        """Categorize content type"""
        text = soup.get_text().lower()
        categories = []
        
        # Simple keyword-based categorization
        category_keywords = {
            'news': ['news', 'update', 'report', 'breaking'],
            'blog': ['blog', 'post', 'article', 'write-up'],
            'ecommerce': ['buy', 'price', 'cart', 'shop', 'product'],
            'technical': ['code', 'programming', 'api', 'documentation'],
            'educational': ['learn', 'tutorial', 'guide', 'how-to']
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in text for keyword in keywords):
                categories.append(category)
        
        return categories if categories else ['general']

    async def _detect_language(self, soup: BeautifulSoup) -> str:
        """Detect page language (simplified)"""
        # In production, this would use language detection libraries
        html_tag = soup.find('html')
        if html_tag and html_tag.get('lang'):
            return html_tag.get('lang')
        
        # Simple English detection
        text = soup.get_text().lower()
        common_english_words = ['the', 'and', 'is', 'in', 'to', 'of', 'a', 'that', 'it', 'with']
        
        english_word_count = sum(1 for word in common_english_words if word in text)
        if english_word_count >= 3:
            return 'en'
        
        return 'unknown'

    # Helper extraction methods
    def _safe_extract(self, soup: BeautifulSoup, selector: str) -> str:
        """Safely extract text from selector"""
        element = soup.select_one(selector)
        return element.get_text(strip=True) if element else ""

    def _extract_meta_description(self, soup: BeautifulSoup) -> str:
        """Extract meta description"""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        return meta_desc.get('content', '') if meta_desc else ""

    def _extract_headings(self, soup: BeautifulSoup) -> Dict[str, List[str]]:
        """Extract all headings"""
        headings = {}
        for level in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            elements = soup.find_all(level)
            headings[level] = [elem.get_text(strip=True) for elem in elements]
        return headings

    def _extract_paragraphs(self, soup: BeautifulSoup) -> List[str]:
        """Extract paragraphs"""
        paragraphs = soup.find_all('p')
        return [p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)]

    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Extract links with text and URLs"""
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            full_url = urljoin(base_url, href)
            links.append({
                'text': a.get_text(strip=True),
                'url': full_url,
                'is_external': urlparse(full_url).netloc != urlparse(base_url).netloc
            })
        return links

    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Extract images with sources and alt text"""
        images = []
        for img in soup.find_all('img', src=True):
            src = img.get('src', '')
            full_src = urljoin(base_url, src)
            images.append({
                'src': full_src,
                'alt': img.get('alt', ''),
                'title': img.get('title', '')
            })
        return images

    def _extract_tables(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract table data"""
        tables = []
        for table in soup.find_all('table'):
            rows = []
            for tr in table.find_all('tr'):
                cells = [td.get_text(strip=True) for td in tr.find_all(['td', 'th'])]
                if cells:
                    rows.append(cells)
            if rows:
                tables.append({
                    'headers': rows[0] if rows else [],
                    'data': rows[1:] if len(rows) > 1 else []
                })
        return tables

    def _extract_lists(self, soup: BeautifulSoup) -> Dict[str, List[List[str]]]:
        """Extract list items"""
        lists = {'ordered': [], 'unordered': []}
        
        for ol in soup.find_all('ol'):
            items = [li.get_text(strip=True) for li in ol.find_all('li')]
            if items:
                lists['ordered'].append(items)
        
        for ul in soup.find_all('ul'):
            items = [li.get_text(strip=True) for li in ul.find_all('li')]
            if items:
                lists['unordered'].append(items)
        
        return lists

    async def _extract_contact_info(self, soup: BeautifulSoup) -> Dict[str, List[str]]:
        """Extract contact information using patterns"""
        text = soup.get_text()
        contact_info = {
            'emails': re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text),
            'phones': re.findall(r'(\+?[\d\s\-\(\)]{7,})', text),
            'addresses': []  # More complex pattern matching would be needed
        }
        return contact_info

    def _extract_social_links(self, soup: BeautifulSoup, base_url: str) -> Dict[str, List[str]]:
        """Extract social media links"""
        social_patterns = {
            'facebook': r'facebook\.com/[^"\']+',
            'twitter': r'twitter\.com/[^"\']+',
            'linkedin': r'linkedin\.com/[^"\']+',
            'instagram': r'instagram\.com/[^"\']+',
            'youtube': r'youtube\.com/[^"\']+'
        }
        
        social_links = {}
        text = soup.get_text()
        
        for platform, pattern in social_patterns.items():
            matches = re.findall(pattern, text)
            full_links = [urljoin(base_url, match) for match in matches]
            social_links[platform] = full_links
        
        return social_links

    # AI-powered extraction methods (would integrate with actual AI in production)
    async def _extract_topics(self, text: str) -> List[str]:
        """Extract main topics from text (simplified)"""
        # This would use NLP in production
        words = text.lower().split()
        common_topics = {
            'technology': ['ai', 'machine', 'learning', 'software', 'code', 'programming'],
            'business': ['company', 'business', 'market', 'sales', 'revenue'],
            'health': ['health', 'medical', 'care', 'doctor', 'hospital'],
            'education': ['learn', 'education', 'school', 'university', 'course']
        }
        
        topics = []
        for topic, keywords in common_topics.items():
            if any(keyword in words for keyword in keywords):
                topics.append(topic)
        
        return topics

    async def _analyze_sentiment(self, text: str) -> str:
        """Analyze text sentiment (simplified)"""
        positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'best']
        negative_words = ['bad', 'terrible', 'awful', 'horrible', 'worst', 'poor']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'

    async def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract named entities (simplified)"""
        # This would use NER in production
        entities = {
            'people': re.findall(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b', text),
            'organizations': re.findall(r'\b[A-Z][a-zA-Z]+ (Inc|Corp|Company|Ltd)\b', text),
            'locations': re.findall(r'\b[A-Z][a-zA-Z]+ (Street|Avenue|Road|City|State)\b', text)
        }
        return entities

    async def _generate_summary(self, text: str) -> str:
        """Generate text summary (simplified)"""
        sentences = re.split(r'[.!?]+', text)
        if len(sentences) >= 3:
            return ' '.join(sentences[:3]) + '...'
        return text[:200] + '...' if len(text) > 200 else text

    async def export_scraped_data(self, data: Dict[str, Any], format: str = 'json') -> str:
        """Export scraped data in various formats"""
        if format == 'json':
            return json.dumps(data, indent=2, ensure_ascii=False)
        elif format == 'csv':
            # Simplified CSV conversion
            csv_lines = []
            for key, value in data.items():
                if isinstance(value, list):
                    csv_lines.append(f"{key},{','.join(map(str, value))}")
                else:
                    csv_lines.append(f"{key},{value}")
            return '\n'.join(csv_lines)
        else:
            return str(data)
