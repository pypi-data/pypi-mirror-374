#!/usr/bin/env python3
"""
Simple test to verify the json parameter fix was applied correctly
"""

import re
from pathlib import Path


def check_file_for_json_parameter_issues(file_path):
    """Check if a file has the problematic json= parameter in put/post calls"""
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Look for .put( or .post( calls with json= parameter
    put_json_pattern = r'\.put\([^)]*json='
    post_json_pattern = r'\.post\([^)]*json='
    
    put_matches = re.findall(put_json_pattern, content)
    post_matches = re.findall(post_json_pattern, content)
    
    issues = []
    if put_matches:
        issues.extend([f"Found .put() with json= parameter: {match}" for match in put_matches])
    if post_matches:
        issues.extend([f"Found .post() with json= parameter: {match}" for match in post_matches])
    
    return issues


def check_file_for_data_parameter(file_path):
    """Check if a file properly uses data= parameter instead of json="""
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Look for .put( or .post( calls with data= parameter
    put_data_pattern = r'\.put\([^)]*data='
    post_data_pattern = r'\.post\([^)]*data='
    
    put_matches = re.findall(put_data_pattern, content)
    post_matches = re.findall(post_data_pattern, content)
    
    return put_matches + post_matches


def main():
    """Main test function"""
    
    print("🔍 Checking for json parameter issues in Jira files...")
    
    # Files to check
    files_to_check = [
        "src/mcp_atlassian/jira/issues.py",
        "src/mcp_atlassian/jira/links.py", 
        "src/mcp_atlassian/jira/client.py"
    ]
    
    all_issues = []
    data_usage_count = 0
    
    for file_path in files_to_check:
        full_path = Path(file_path)
        if not full_path.exists():
            print(f"❌ File not found: {file_path}")
            continue
            
        print(f"📁 Checking {file_path}...")
        
        # Check for problematic json= usage
        issues = check_file_for_json_parameter_issues(full_path)
        if issues:
            print(f"❌ Issues found in {file_path}:")
            for issue in issues:
                print(f"   - {issue}")
            all_issues.extend(issues)
        else:
            print(f"✅ No json= parameter issues in {file_path}")
        
        # Check for correct data= usage
        data_matches = check_file_for_data_parameter(full_path)
        if data_matches:
            print(f"✅ Found {len(data_matches)} correct data= parameter usage(s) in {file_path}")
            data_usage_count += len(data_matches)
    
    print("\n" + "="*60)
    
    if all_issues:
        print(f"❌ FAILED: Found {len(all_issues)} json= parameter issues that need to be fixed:")
        for issue in all_issues:
            print(f"   - {issue}")
        return False
    else:
        print(f"✅ SUCCESS: No json= parameter issues found!")
        print(f"✅ Found {data_usage_count} correct data= parameter usage(s)")
        print("✅ The fix has been applied correctly!")
        print("\n🎉 The MCP server should now work without 'json' parameter errors!")
        return True


if __name__ == "__main__":
    import sys
    result = main()
    sys.exit(0 if result else 1)
