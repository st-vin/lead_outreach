import pandas as pd
import re
from application.utils.phone import normalize_phone, is_phone_like
import config

class DataCleaner:
    """Service for cleaning and normalizing CSV data with confidence scoring"""
    
    def __init__(self, country_code='+254', region='KE'):
        self.country_code = country_code
        self.region = region
    
    def is_valid_business_name(self, name):
        """Check if value looks like a valid business name"""
        if not name or str(name).strip() == '':
            return False
        str_name = str(name).strip()
        if len(str_name) < 2 or len(str_name) > 200:
            return False
        if str_name.replace('.', '').isdigit():  # Just numbers
            return False
        return True
    
    def count_valid_names(self, sample_data):
        """Count how many values look like business names"""
        return sum(1 for val in sample_data if self.is_valid_business_name(val))
    
    def count_phone_like(self, sample_data):
        """Count how many values look like phone numbers"""
        return sum(1 for val in sample_data if is_phone_like(val))
    
    def count_numeric_range(self, sample_data, min_val=0, max_val=5):
        """Count how many values are numeric in range (for ratings)"""
        count = 0
        for val in sample_data:
            try:
                num = float(val)
                if min_val <= num <= max_val:
                    count += 1
            except:
                pass
        return count
    
    def detect_columns_with_confidence(self, df):
        """
        Auto-detect column mappings with confidence scores
        
        Returns:
            dict: Mapping of field names to detected columns with confidence
        """
        column_mappings = {}
        
        # Patterns to match column names
        name_patterns = ['name', 'business', 'company', 'qBF1Pd']
        phone_patterns = ['phone', 'tel', 'contact', 'mobile', 'Cw1rxd']
        rating_patterns = ['rating', 'star', 'score', 'MW4etd']
        review_patterns = ['review', 'count', 'UY7F9']
        category_patterns = ['category', 'type', 'W4Efsd']
        website_patterns = ['website', 'url', 'site', 'lcr4fd']
        address_patterns = ['address', 'location', 'W4Efsd']
        maps_patterns = ['href', 'link', 'hfpxzc', 'maps']
        snippet_patterns = ['snippet', 'comment', 'ah5Ghc']
        
        for col in df.columns:
            col_lower = str(col).lower()
            sample_data = df[col].dropna().head(10)
            
            if len(sample_data) == 0:
                continue
            
            confidence_scores = {}
            
            # Check business name
            if any(p in col_lower for p in name_patterns):
                valid_count = self.count_valid_names(sample_data)
                confidence_scores['business_name'] = valid_count / len(sample_data)
            
            # Check phone
            if any(p in col_lower for p in phone_patterns):
                valid_count = self.count_phone_like(sample_data)
                confidence_scores['phone'] = valid_count / len(sample_data)
            
            # Check rating
            if any(p in col_lower for p in rating_patterns):
                valid_count = self.count_numeric_range(sample_data, 0, 5)
                confidence_scores['rating'] = valid_count / len(sample_data)
            
            # Check review count
            if any(p in col_lower for p in review_patterns):
                # Look for numbers in parentheses like "(5)"
                valid_count = sum(1 for val in sample_data if re.search(r'\d+', str(val)))
                confidence_scores['review_count'] = valid_count / len(sample_data)
            
            # Check category
            if any(p in col_lower for p in category_patterns):
                # Categories are typically short text
                valid_count = sum(1 for val in sample_data if 2 < len(str(val)) < 50)
                confidence_scores['category'] = valid_count / len(sample_data)
            
            # Check website
            if any(p in col_lower for p in website_patterns):
                valid_count = sum(1 for val in sample_data if 'http' in str(val).lower() or '.' in str(val))
                confidence_scores['website'] = valid_count / len(sample_data) if valid_count > 0 else 0.3
            
            # Check maps URL
            if any(p in col_lower for p in maps_patterns):
                valid_count = sum(1 for val in sample_data if 'maps' in str(val).lower() or 'http' in str(val).lower())
                confidence_scores['google_maps_url'] = valid_count / len(sample_data) if valid_count > 0 else 0.3
            
            # Pick best match if confidence is high enough
            if confidence_scores:
                best_field, confidence = max(confidence_scores.items(), key=lambda x: x[1])
                
                if confidence >= config.COLUMN_CONFIDENCE_THRESHOLD:
                    column_mappings[best_field] = {
                        'csv_column': col,
                        'confidence': confidence,
                        'sample_values': sample_data.head(3).tolist()
                    }
        
        return column_mappings
    
    def merge_address_columns(self, row, detected_mappings):
        """Merge fragmented address columns"""
        address_parts = []
        
        # If we have a specific address mapping, use it
        if 'address' in detected_mappings:
            addr_col = detected_mappings['address']['csv_column']
            if addr_col in row.index:
                value = str(row[addr_col]).strip()
                if value and value != 'nan':
                    return value
        
        # Otherwise, look for W4Efsd columns (address fragments)
        for col in row.index:
            if 'W4Efsd' in col:
                value = str(row[col]).strip()
                if value and value != '·' and value != 'nan' and value != '':
                    address_parts.append(value)
        
        return ', '.join(filter(None, address_parts)) if address_parts else ''
    
    def clean_rating(self, rating_str):
        """Extract numeric rating from string"""
        if pd.isna(rating_str):
            return None
        clean = str(rating_str).replace('(', '').replace(')', '').strip()
        try:
            return float(clean)
        except (ValueError, TypeError):
            return None
    
    def clean_review_count(self, count_str):
        """Extract numeric review count from string"""
        if pd.isna(count_str):
            return 0
        match = re.search(r'\d+', str(count_str))
        if match:
            return int(match.group())
        return 0
    
    def validate_and_clean_business(self, row_data, detected_mappings):
        """
        Validate and clean a single business row
        
        Returns:
            tuple: (business_dict, skip_reason)
            business_dict is None if should be skipped
        """
        business = {}
        
        # Extract business name
        if 'business_name' not in detected_mappings:
            return None, "No business name column detected"
        
        name_col = detected_mappings['business_name']['csv_column']
        business['name'] = str(row_data.get(name_col, '')).strip()
        
        if not self.is_valid_business_name(business['name']):
            return None, f"Invalid business name: {business['name']}"
        
        # Extract and validate phone
        phone_raw = ''
        if 'phone' in detected_mappings:
            phone_col = detected_mappings['phone']['csv_column']
            phone_raw = str(row_data.get(phone_col, '')).strip()
        
        business['phone_raw'] = phone_raw if phone_raw != 'nan' else ''
        business['phone_normalized'] = normalize_phone(phone_raw, self.country_code, self.region)
        
        if not business['phone_normalized']:
            return None, f"Invalid or missing phone number: {phone_raw}"
        
        # Extract other fields (these can be empty)
        if 'category' in detected_mappings:
            cat_col = detected_mappings['category']['csv_column']
            business['category'] = str(row_data.get(cat_col, '')).strip()
        else:
            business['category'] = ''
        
        # Rating
        if 'rating' in detected_mappings:
            rating_col = detected_mappings['rating']['csv_column']
            business['rating'] = self.clean_rating(row_data.get(rating_col))
        else:
            business['rating'] = None
        
        # Review count
        if 'review_count' in detected_mappings:
            review_col = detected_mappings['review_count']['csv_column']
            business['review_count'] = self.clean_review_count(row_data.get(review_col))
        else:
            business['review_count'] = 0
        
        # Website
        if 'website' in detected_mappings:
            web_col = detected_mappings['website']['csv_column']
            website_raw = str(row_data.get(web_col, '')).strip()
            business['website_url'] = website_raw if website_raw and website_raw != 'nan' else None
        else:
            business['website_url'] = None
        
        # Google Maps URL
        if 'google_maps_url' in detected_mappings:
            maps_col = detected_mappings['google_maps_url']['csv_column']
            maps_raw = str(row_data.get(maps_col, '')).strip()
            business['google_maps_url'] = maps_raw if maps_raw and maps_raw != 'nan' else None
        else:
            business['google_maps_url'] = None
        
        # Review snippet
        if 'review_snippet' in detected_mappings:
            snippet_col = detected_mappings['review_snippet']['csv_column']
            snippet = str(row_data.get(snippet_col, '')).strip()
            business['review_snippet'] = snippet if snippet and snippet != 'nan' else None
        else:
            business['review_snippet'] = None
        
        # Address (merge fragments)
        business['address'] = self.merge_address_columns(row_data, detected_mappings)
        
        return business, None
    
    def clean_and_validate_dataframe(self, df, detected_mappings):
        """
        Clean and validate entire dataframe
        
        Returns:
            dict with 'valid_businesses', 'skipped_businesses', 'stats'
        """
        valid_businesses = []
        skipped_businesses = []
        
        for idx, row in df.iterrows():
            business, skip_reason = self.validate_and_clean_business(row, detected_mappings)
            
            if business:
                valid_businesses.append(business)
            else:
                skipped_businesses.append({
                    'row_number': idx + 2,  # +2 for Excel (header=1, 0-indexed)
                    'name': str(row.get(detected_mappings.get('business_name', {}).get('csv_column', ''), 'Unknown')),
                    'reason': skip_reason,
                    'phone_raw': str(row.get(detected_mappings.get('phone', {}).get('csv_column', ''), '')).strip()
                })
        
        # Group skip reasons
        skip_reasons_count = {}
        for skipped in skipped_businesses:
            reason = skipped['reason']
            skip_reasons_count[reason] = skip_reasons_count.get(reason, 0) + 1
        
        stats = {
            'total_rows': len(df),
            'valid_count': len(valid_businesses),
            'skipped_count': len(skipped_businesses),
            'skip_reasons': skip_reasons_count
        }
        
        return {
            'valid_businesses': valid_businesses,
            'skipped_businesses': skipped_businesses[:50],  # Limit to first 50 for display
            'stats': stats
        }
