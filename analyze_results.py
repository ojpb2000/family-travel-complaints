#!/usr/bin/env python3
import csv
import random

# Read the classified results and filter for legitimate hotel complaints
results = []
with open('Classified_Complaints.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    results = list(reader)

# Filter for hotel/travel related content, excluding 'Not Relevant'
hotel_keywords = ['hotel', 'resort', 'room', 'stay', 'booking', 'check-in', 'travel', 'vacation', 'pool', 'restaurant', 'tripadvisor']

legitimate_complaints = []
for result in results:
    text_lower = result['Sound_Bite_Text'].lower()
    if (any(keyword in text_lower for keyword in hotel_keywords) and 
        result['Primary_Category'] != 'Not Relevant'):
        legitimate_complaints.append(result)

print(f'LEGITIMATE HOTEL COMPLAINTS: {len(legitimate_complaints)} entries')
print('=' * 60)

# Category distribution for legitimate complaints
complaint_categories = {}
for result in legitimate_complaints:
    primary = result['Primary_Category']
    complaint_categories[primary] = complaint_categories.get(primary, 0) + 1

print('\nLEGITIMATE COMPLAINTS - Category Distribution:')
for category, count in sorted(complaint_categories.items(), key=lambda x: x[1], reverse=True):
    percentage = (count / len(legitimate_complaints)) * 100
    print(f'  {category}: {count} ({percentage:.1f}%)')

# Show examples from each complaint category
categories = ['Room Quality Issues', 'Food & Dining Problems', 'Service Issues', 'Facility Problems', 
              'Family Experience Issues', 'Booking & Check-in Problems', 'Value Concerns', 
              'Noise & Environment', 'Safety & Security']

print('\n' + '=' * 60)
print('SAMPLE LEGITIMATE HOTEL COMPLAINTS BY CATEGORY:')
print('=' * 60)

for category in categories:
    category_items = [r for r in legitimate_complaints if r['Primary_Category'] == category]
    if category_items:
        # Show 1-2 examples per category
        samples = random.sample(category_items, min(2, len(category_items)))
        print(f'\n{category.upper()} ({len(category_items)} entries):')
        for i, sample in enumerate(samples, 1):
            print(f'  Example {i} (Row {sample["Row_Number"]}):')
            print(f'    Text: {sample["Sound_Bite_Text"][:150]}...')
            print(f'    Reason: {sample["Classification_Reason"]}')
            if sample['Secondary_Category']:
                print(f'    Secondary: {sample["Secondary_Category"]}')