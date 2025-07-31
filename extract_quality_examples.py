#!/usr/bin/env python3
import csv
import sys
import re
from collections import defaultdict

def is_travel_related(sound_bite, title, url):
    """Check if the content is actually travel/hotel related"""
    travel_keywords = ['hotel', 'resort', 'trip', 'vacation', 'stay', 'accommodation', 'travel', 'room', 'booking', 'check-in']
    travel_domains = ['tripadvisor', 'booking', 'opentable', 'hotels', 'expedia', 'airbnb']
    
    combined_text = (sound_bite + " " + title + " " + url).lower()
    
    # Must have travel keywords
    if not any(keyword in combined_text for keyword in travel_keywords):
        return False
    
    # Must be from travel-related domains or contain clear travel indicators
    if not any(domain in url.lower() for domain in travel_domains):
        if not any(keyword in combined_text for keyword in ['stayed', 'hotel', 'resort', 'room']):
            return False
    
    return True

def is_legitimate_complaint(sound_bite):
    """Check if this is a legitimate complaint (not positive review)"""
    negative_indicators = ['disappointed', 'terrible', 'awful', 'bad', 'worst', 'horrible', 'disgusting', 
                          'dirty', 'unclean', 'rude', 'poor', 'complaint', 'problem', 'issue', 'annoying',
                          'frustrated', 'upset', 'angry', 'avoid', 'waste', 'overpriced', 'expensive']
    
    positive_only = ['excellent', 'wonderful', 'amazing', 'fantastic', 'perfect', 'loved', 'great', 'brilliant']
    
    text_lower = sound_bite.lower()
    
    # Must have negative indicators
    has_negative = any(word in text_lower for word in negative_indicators)
    
    # Check if it's only positive (no complaints)
    only_positive = (any(word in text_lower for word in positive_only) and 
                    not has_negative)
    
    return has_negative and not only_positive

def clean_text(text):
    """Clean and truncate text for display"""
    if not text:
        return ""
    # Remove extra quotes and clean up
    text = text.strip().strip('"').strip("'")
    # Remove review metadata
    text = re.sub(r'Date of stay:.*?Trip type:.*?>', '', text)
    text = re.sub(r'Ask \w+ about.*?Thank \w+', '', text)
    text = re.sub(r'This review is the subjective opinion.*?$', '', text)
    # Limit length for readability
    if len(text) > 250:
        text = text[:247] + "..."
    return text.strip()

def extract_cultural_insight(sound_bite, classification):
    """Extract cultural gap or pattern insight"""
    sound_bite_lower = sound_bite.lower()
    
    if 'food poisoning' in sound_bite_lower or 'stomach' in sound_bite_lower:
        return "Health and safety concerns paramount for family travel"
    elif 'dirty' in sound_bite_lower or 'not cleaned' in sound_bite_lower:
        return "Cleanliness standards critical for family accommodations"
    elif ('staff' in sound_bite_lower and ('rude' in sound_bite_lower or 'demanding' in sound_bite_lower)) or 'service' in sound_bite_lower:
        return "Service attitude impacts family vacation satisfaction"
    elif 'money' in sound_bite_lower or 'expensive' in sound_bite_lower or 'waste' in sound_bite_lower or 'overpriced' in sound_bite_lower:
        return "Value consciousness heightened when traveling with family"
    elif 'noise' in sound_bite_lower or 'loud' in sound_bite_lower:
        return "Family travelers sensitive to noise disruptions"
    elif 'booking' in sound_bite_lower or 'reservation' in sound_bite_lower or 'check-in' in sound_bite_lower:
        return "Booking complications especially stressful for family groups"
    elif 'facility' in sound_bite_lower or 'closed' in sound_bite_lower or 'pool' in sound_bite_lower:
        return "Facility availability crucial for family vacation planning"
    elif 'kids' in sound_bite_lower or 'children' in sound_bite_lower:
        return "Child-centric travel expectations and specific needs"
    elif 'disappointed' in sound_bite_lower:
        return "High expectations for family experiences, disappointment when reality doesn't match"
    else:
        return "General family travel expectations and service standards"

def is_quality_example(row):
    """Determine if this is a quality example"""
    sound_bite = row.get('Sound Bite Text', '').strip()
    url = row.get('URL', '').strip()
    title = row.get('Title', '').strip()
    
    # Must have all required fields
    if not all([sound_bite, url, title]):
        return False
    
    # Must be substantial complaint
    if len(sound_bite) < 30:
        return False
    
    # Must mention family travel
    if not any(word in sound_bite.lower() for word in ['family', 'kids', 'children']):
        return False
    
    # Must be travel related
    if not is_travel_related(sound_bite, title, url):
        return False
    
    # Must be a legitimate complaint
    if not is_legitimate_complaint(sound_bite):
        return False
    
    return True

def main():
    # Read the CSV file
    examples_by_category = defaultdict(list)
    
    categories = [
        'Room Quality Issues',
        'Family Experience Issues', 
        'Service Issues',
        'Food & Dining Problems',
        'Facility Problems',
        'Value Concerns',
        'Safety & Security',
        'Booking & Check-in Problems',
        'Noise & Environment'
    ]
    
    with open('/mnt/d/TBWA/Other_SL/Complains_Expand_Classified.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            category = row.get('Primary_Category', '').strip()
            
            if category in categories and is_quality_example(row):
                examples_by_category[category].append(row)
    
    # Extract 10 quality examples for each category
    for category in categories:
        examples = examples_by_category[category]
        total_count = len([row for row in examples if is_quality_example(row)])
        
        print(f"\n{'='*60}")
        print(f"{category.upper()} ({total_count} quality examples in database)")
        print(f"{'='*60}")
        
        # Take up to 10 diverse examples
        selected_examples = []
        used_domains = set()
        used_keywords = set()
        
        for example in examples:
            if len(selected_examples) >= 10:
                break
                
            sound_bite = example.get('Sound Bite Text', '').strip()
            url = example.get('URL', '').strip()
            
            # Get domain for diversity
            domain = url.split('/')[2] if '/' in url else ''
            
            # Get key complaint words for diversity
            key_words = set(word.lower() for word in re.findall(r'\b\w+\b', sound_bite) 
                          if word.lower() in ['dirty', 'clean', 'staff', 'food', 'room', 'noise', 
                                            'booking', 'expensive', 'facility', 'rude', 'disappointed'])
            
            # Prefer diverse domains and complaint types
            if (domain not in used_domains or len(selected_examples) < 5) and \
               (not key_words.intersection(used_keywords) or len(selected_examples) < 3):
                selected_examples.append(example)
                used_domains.add(domain)
                used_keywords.update(key_words)
        
        # If we don't have 10, fill with remaining examples
        if len(selected_examples) < 10:
            for example in examples:
                if len(selected_examples) >= 10:
                    break
                if example not in selected_examples:
                    selected_examples.append(example)
        
        for i, example in enumerate(selected_examples, 1):
            sound_bite = clean_text(example.get('Sound Bite Text', ''))
            title = clean_text(example.get('Title', ''))
            url = example.get('URL', '').strip()
            country = example.get('Author Location - Country 1', '').strip() or 'Not specified'
            classification = example.get('Classification_Reason', '').strip()
            
            cultural_insight = extract_cultural_insight(sound_bite, classification)
            
            print(f"\n{i}. Sound Bite: \"{sound_bite}\"")
            print(f"   Source: {title}")
            print(f"   URL: {url}")
            print(f"   Location: {country}")
            print(f"   Cultural Gap/Pattern: {cultural_insight}")

if __name__ == "__main__":
    main()