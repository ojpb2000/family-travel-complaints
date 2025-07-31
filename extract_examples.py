#!/usr/bin/env python3
import csv
import sys
import re
from collections import defaultdict

def clean_text(text):
    """Clean and truncate text for display"""
    if not text:
        return ""
    # Remove extra quotes and clean up
    text = text.strip().strip('"').strip("'")
    # Limit length for readability
    if len(text) > 300:
        text = text[:297] + "..."
    return text

def extract_cultural_insight(sound_bite, classification):
    """Extract cultural gap or pattern insight"""
    sound_bite_lower = sound_bite.lower()
    
    if 'family' in sound_bite_lower and 'disappointed' in sound_bite_lower:
        return "High expectations for family experiences, disappointment when reality doesn't match"
    elif 'kids' in sound_bite_lower or 'children' in sound_bite_lower:
        return "Child-centric travel expectations and specific needs"
    elif 'food poisoning' in sound_bite_lower or 'stomach' in sound_bite_lower:
        return "Health and safety concerns paramount for family travel"
    elif 'dirty' in sound_bite_lower or 'clean' in sound_bite_lower:
        return "Cleanliness standards critical for family accommodations"
    elif 'staff' in sound_bite_lower and ('rude' in sound_bite_lower or 'unfriendly' in sound_bite_lower):
        return "Service attitude impacts family vacation satisfaction"
    elif 'money' in sound_bite_lower or 'expensive' in sound_bite_lower or 'waste' in sound_bite_lower:
        return "Value consciousness heightened when traveling with family"
    elif 'noise' in sound_bite_lower or 'loud' in sound_bite_lower:
        return "Family travelers sensitive to noise disruptions"
    elif 'booking' in sound_bite_lower or 'reservation' in sound_bite_lower:
        return "Booking complications especially stressful for family groups"
    elif 'facility' in sound_bite_lower or 'closed' in sound_bite_lower:
        return "Facility availability crucial for family vacation planning"
    else:
        return "General family travel expectations and service standards"

def is_quality_example(row):
    """Determine if this is a quality example"""
    sound_bite = row.get('Sound Bite Text', '').strip()
    url = row.get('URL', '').strip()
    title = row.get('Title', '').strip()
    country = row.get('Author Location - Country 1', '').strip()
    
    # Must have all required fields
    if not all([sound_bite, url, title]):
        return False
    
    # Must be substantial complaint
    if len(sound_bite) < 50:
        return False
    
    # Must mention family travel
    if 'family' not in sound_bite.lower() and 'kids' not in sound_bite.lower() and 'children' not in sound_bite.lower():
        return False
    
    # Must be a complaint (not positive review)
    positive_indicators = ['excellent', 'wonderful', 'amazing', 'fantastic', 'perfect', 'loved']
    if any(word in sound_bite.lower() for word in positive_indicators) and not any(word in sound_bite.lower() for word in ['disappointed', 'terrible', 'awful', 'bad', 'worst']):
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
        total_count = len(examples)
        
        print(f"\n{'='*60}")
        print(f"{category.upper()} ({total_count} total in database)")
        print(f"{'='*60}")
        
        # Take up to 10 diverse examples
        selected_examples = []
        used_keywords = set()
        
        for example in examples:
            if len(selected_examples) >= 10:
                break
                
            sound_bite = example.get('Sound Bite Text', '').strip()
            
            # Try to get diverse examples by avoiding similar keywords
            key_words = set(word.lower() for word in re.findall(r'\b\w+\b', sound_bite) 
                          if len(word) > 4 and word.lower() in ['dirty', 'clean', 'staff', 'food', 'room', 'noise', 'booking', 'expensive', 'facility'])
            
            if not key_words or not key_words.intersection(used_keywords) or len(selected_examples) < 5:
                selected_examples.append(example)
                used_keywords.update(key_words)
        
        # If we don't have 10, just take the first 10
        if len(selected_examples) < 10:
            selected_examples = examples[:10]
        
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