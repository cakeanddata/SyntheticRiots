#!/usr/bin/env python3
"""
Location Mention Analyzer for Debate Transcripts
Matches location mentions in text with Northern Ireland locations database
"""

import re
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
from pathlib import Path

def load_locations():
    """Load location data and create search patterns"""
    # Load locations dictionary
    with open("ni_locations_dict.json", "r") as f:
        locations_dict = json.load(f)
    
    # Load main dataframe for visualization
    df = pd.read_csv("ni_locations.csv")
    
    return locations_dict, df

def find_location_mentions(text, locations_dict):
    """Find all location mentions in text"""
    text_lower = text.lower()
    mentions = []
    
    # Track which locations have been found to avoid duplicates
    found_locations = set()
    
    for search_term, location_info in locations_dict.items():
        # Create word boundary pattern to avoid partial matches
        # This prevents matching "down" in "downtown" when looking for County Down
        pattern = r'\b' + re.escape(search_term) + r'\b'
        
        # Find all matches
        matches = re.finditer(pattern, text_lower)
        
        for match in matches:
            official_name = location_info['official_name']
            
            # Record the mention
            mentions.append({
                'matched_text': search_term,
                'official_name': official_name,
                'location_type': location_info['type'],
                'position': match.start(),
                'context': text[max(0, match.start()-50):min(len(text), match.end()+50)]
            })
            
            found_locations.add(official_name)
    
    return mentions

def analyze_debate_locations(transcript_file="debate_transcript_clean.txt"):
    """Analyze location mentions in debate transcript"""
    
    # Load transcript
    if not Path(transcript_file).exists():
        print(f"⚠️ Transcript file {transcript_file} not found. Run debate_pull.py first.")
        return None
    
    with open(transcript_file, "r", encoding="utf-8") as f:
        transcript = f.read()
    
    # Load locations
    locations_dict, locations_df = load_locations()
    
    # Find mentions
    print("🔍 Searching for location mentions in transcript...")
    mentions = find_location_mentions(transcript, locations_dict)
    
    if not mentions:
        print("No location mentions found in transcript.")
        return None
    
    # Convert to DataFrame for analysis
    mentions_df = pd.DataFrame(mentions)
    
    # Count mentions by official name
    location_counts = mentions_df['official_name'].value_counts()
    
    # Add region type information
    type_counts = mentions_df.groupby(['official_name', 'location_type']).size().reset_index(name='count')
    
    # Save results
    mentions_df.to_csv("debate_location_mentions.csv", index=False)
    print(f"✅ Saved detailed mentions to debate_location_mentions.csv")
    
    # Save summary
    summary = {
        'total_mentions': len(mentions),
        'unique_locations': len(location_counts),
        'top_10_locations': location_counts.head(10).to_dict(),
        'mentions_by_type': mentions_df['location_type'].value_counts().to_dict()
    }
    
    with open("debate_location_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n📊 Location Analysis Summary:")
    print(f"   Total mentions: {summary['total_mentions']}")
    print(f"   Unique locations: {summary['unique_locations']}")
    
    print(f"\n🏆 Top 10 Most Mentioned Locations:")
    for loc, count in location_counts.head(10).items():
        print(f"   {loc}: {count} mentions")
    
    return mentions_df, location_counts

def create_location_visualizations(mentions_df=None, location_counts=None):
    """Create visualizations of location mentions"""
    
    if mentions_df is None:
        # Try to load from saved file
        if Path("debate_location_mentions.csv").exists():
            mentions_df = pd.read_csv("debate_location_mentions.csv")
            location_counts = mentions_df['official_name'].value_counts()
        else:
            print("No data available for visualization. Run analysis first.")
            return
    
    # Set style
    plt.style.use('seaborn-v0_8-darkgrid')
    sns.set_palette("husl")
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    
    # 1. Top locations bar chart
    ax1 = axes[0, 0]
    top_15 = location_counts.head(15)
    top_15.plot(kind='barh', ax=ax1)
    ax1.set_title('Top 15 Most Mentioned Locations', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Number of Mentions')
    ax1.set_ylabel('Location')
    
    # 2. Mentions by location type
    ax2 = axes[0, 1]
    type_counts = mentions_df['location_type'].value_counts()
    colors = plt.cm.Set3(range(len(type_counts)))
    type_counts.plot(kind='pie', ax=ax2, autopct='%1.1f%%', colors=colors)
    ax2.set_title('Distribution of Mentions by Location Type', fontsize=14, fontweight='bold')
    ax2.set_ylabel('')
    
    # 3. Timeline of mentions (if we can extract that from positions)
    ax3 = axes[1, 0]
    # Divide transcript into segments and count mentions
    mentions_df['segment'] = pd.cut(mentions_df['position'], bins=20, labels=False)
    timeline = mentions_df.groupby('segment').size()
    timeline.plot(kind='line', ax=ax3, marker='o')
    ax3.set_title('Location Mentions Throughout Debate', fontsize=14, fontweight='bold')
    ax3.set_xlabel('Debate Progress (segments)')
    ax3.set_ylabel('Number of Mentions')
    ax3.grid(True, alpha=0.3)
    
    # 4. Focus on specific region types
    ax4 = axes[1, 1]
    # Group by type and get top locations for each
    type_top = {}
    for loc_type in mentions_df['location_type'].unique():
        type_df = mentions_df[mentions_df['location_type'] == loc_type]
        type_top[loc_type] = type_df['official_name'].value_counts().head(3).sum()
    
    type_series = pd.Series(type_top)
    type_series.plot(kind='bar', ax=ax4)
    ax4.set_title('Total Mentions by Location Category', fontsize=14, fontweight='bold')
    ax4.set_xlabel('Location Type')
    ax4.set_ylabel('Total Mentions (Top 3 locations per type)')
    ax4.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig('debate_location_analysis.png', dpi=300, bbox_inches='tight')
    print("✅ Saved visualization to debate_location_analysis.png")
    
    plt.show()
    
    # Create a focused Belfast analysis if Belfast is mentioned
    belfast_mentions = mentions_df[mentions_df['official_name'].str.contains('Belfast', na=False)]
    if len(belfast_mentions) > 0:
        fig2, ax = plt.subplots(figsize=(10, 6))
        belfast_areas = belfast_mentions['official_name'].value_counts()
        belfast_areas.plot(kind='bar', ax=ax)
        ax.set_title('Belfast Area Mentions in Debate', fontsize=14, fontweight='bold')
        ax.set_xlabel('Belfast Area')
        ax.set_ylabel('Number of Mentions')
        ax.tick_params(axis='x', rotation=45)
        plt.tight_layout()
        plt.savefig('debate_belfast_analysis.png', dpi=300, bbox_inches='tight')
        print("✅ Saved Belfast-specific analysis to debate_belfast_analysis.png")
        plt.show()

def main():
    """Main analysis function"""
    # Analyze debate transcript
    mentions_df, location_counts = analyze_debate_locations()
    
    if mentions_df is not None:
        # Create visualizations
        create_location_visualizations(mentions_df, location_counts)
        
        # Generate report
        print("\n📋 Analysis Complete!")
        print("Generated files:")
        print("   - debate_location_mentions.csv (detailed mentions)")
        print("   - debate_location_summary.json (summary statistics)")
        print("   - debate_location_analysis.png (main visualizations)")
        print("   - debate_belfast_analysis.png (Belfast focus, if applicable)")

if __name__ == "__main__":
    main()
