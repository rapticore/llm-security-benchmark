#!/usr/bin/env python3
"""
Consolidation Testing & Validation Script

Tests the consolidated modules to ensure all functionality works correctly
after removing redundant files.

Built by the Rapticore Security Research Team
"""

import sys
import traceback
from pathlib import Path
from typing import Dict, List, Any


def test_imports():
    """Test that all consolidated modules can be imported successfully."""
    print("🔍 Testing Consolidated Module Imports...")
    
    tests = [
        ("enhanced_cost_effectiveness_consolidated", "ConsolidatedCostEffectivenessAnalyzer"),
        ("consolidated_reporting_enhanced", "ConsolidatedEnhancedReporter"),
        ("improved_chart_generation_consolidated", "integrate_improved_charts"),
        ("enhanced_data_capture", "EnhancedDataCapture"),
        ("quality_first_audit", "QualityFirstAuditor"),
    ]
    
    results = {}
    
    for module_name, class_name in tests:
        try:
            module = __import__(module_name)
            if hasattr(module, class_name):
                results[module_name] = "✅ PASS"
                print(f"   ✅ {module_name}: {class_name} imported successfully")
            else:
                results[module_name] = "❌ FAIL - Class not found"
                print(f"   ❌ {module_name}: {class_name} not found in module")
        except ImportError as e:
            results[module_name] = f"❌ FAIL - Import error: {e}"
            print(f"   ❌ {module_name}: Import failed - {e}")
        except Exception as e:
            results[module_name] = f"❌ FAIL - Unexpected error: {e}"
            print(f"   ❌ {module_name}: Unexpected error - {e}")
    
    return results


def test_backward_compatibility():
    """Test that backward compatibility functions work."""
    print("\n🔄 Testing Backward Compatibility Functions...")
    
    try:
        from enhanced_cost_effectiveness_consolidated import (
            apply_aggressive_fixes, integrate_enhanced_effectiveness, create_enhanced_effectiveness_report
        )
        print("   ✅ Enhanced cost-effectiveness backward compatibility functions available")
        
        from consolidated_reporting_enhanced import (
            generate_comprehensive_executive_summary, clean_up_redundant_reports,
            generate_unified_report, consolidate_reporting_files
        )
        print("   ✅ Consolidated reporting backward compatibility functions available")
        
        from improved_chart_generation_consolidated import integrate_improved_charts
        print("   ✅ Improved chart generation backward compatibility functions available")
        
        return True
        
    except ImportError as e:
        print(f"   ❌ Backward compatibility test failed: {e}")
        return False


def test_functionality():
    """Test basic functionality of consolidated modules."""
    print("\n⚙️ Testing Basic Functionality...")
    
    try:
        # Test cost-effectiveness analyzer
        from enhanced_cost_effectiveness_consolidated import ConsolidatedCostEffectivenessAnalyzer
        
        analyzer = ConsolidatedCostEffectivenessAnalyzer()
        print("   ✅ ConsolidatedCostEffectivenessAnalyzer initialized")
        
        # Test response quality analysis
        test_response = "This code has a SQL injection vulnerability due to improper input sanitization. Use parameterized queries to prevent this attack."
        quality_metrics = analyzer.analyze_response_quality(test_response, "sql_injection")
        
        if quality_metrics.word_count > 0 and quality_metrics.completeness_score > 0:
            print("   ✅ Response quality analysis working")
        else:
            print("   ❌ Response quality analysis not working properly")
            return False
        
        # Test consolidated reporter
        from consolidated_reporting_enhanced import ConsolidatedEnhancedReporter
        
        reporter = ConsolidatedEnhancedReporter()
        print("   ✅ ConsolidatedEnhancedReporter initialized")
        
        # Test language classification
        language = reporter._classify_language("python_code_injection")
        if language == "Python":
            print("   ✅ Language classification working")
        else:
            print(f"   ❌ Language classification failed: expected 'Python', got '{language}'")
            return False
        
        # Test OWASP classification
        category = reporter._classify_owasp_category("sql_injection_simple")
        if "Injection" in category:
            print("   ✅ OWASP classification working")
        else:
            print(f"   ❌ OWASP classification failed: expected 'Injection', got '{category}'")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Functionality test failed: {e}")
        traceback.print_exc()
        return False


def test_missing_files():
    """Test that redundant files have been properly removed."""
    print("\n🗑️ Testing Redundant File Removal...")
    
    # Files that should be removed
    removed_files = [
        "COMPREHENSIVE_FIXES_SUMMARY.md",
        "ERROR_FIXES_SUMMARY.md",
        "FIXES_IMPLEMENTED.md",
        "FIXES_SUMMARY.md",
        "ENHANCED_REPORTING_SUMMARY.md",
        "REPORT_CONSOLIDATION_SOLUTION.md",
        "LEGACY_REPORT_ISSUE_FIX.md",
        "deepseek_cost_calculation.py",
        "clean_executive_function.py",
        "test_suites/security_basic_broken.yaml"
    ]
    
    # Files that should still exist
    existing_files = [
        "enhanced_cost_effectiveness_consolidated.py",
        "consolidated_reporting_enhanced.py",
        "improved_chart_generation_consolidated.py",
        "enhanced_data_capture.py",
        "quality_first_audit.py",
        "quality_first_reporting.py"
    ]
    
    results = {}
    
    # Check removed files
    for file_path in removed_files:
        if Path(file_path).exists():
            results[file_path] = "❌ FAIL - File still exists"
            print(f"   ❌ {file_path}: File still exists (should be removed)")
        else:
            results[file_path] = "✅ PASS - File properly removed"
            print(f"   ✅ {file_path}: File properly removed")
    
    # Check existing files
    for file_path in existing_files:
        if Path(file_path).exists():
            results[file_path] = "✅ PASS - File exists"
            print(f"   ✅ {file_path}: File exists")
        else:
            results[file_path] = "❌ FAIL - File missing"
            print(f"   ❌ {file_path}: File missing")
    
    return results


def test_backup_integrity():
    """Test that backup files are properly stored."""
    print("\n💾 Testing Backup Integrity...")
    
    backup_dir = Path("backup_redundant_files")
    if not backup_dir.exists():
        print("   ❌ Backup directory does not exist")
        return False
    
    expected_backup_files = [
        "COMPREHENSIVE_FIXES_SUMMARY.md",
        "ERROR_FIXES_SUMMARY.md",
        "FIXES_IMPLEMENTED.md",
        "FIXES_SUMMARY.md",
        "ENHANCED_REPORTING_SUMMARY.md",
        "REPORT_CONSOLIDATION_SOLUTION.md",
        "LEGACY_REPORT_ISSUE_FIX.md",
        "deepseek_cost_calculation.py",
        "clean_executive_function.py",
        "security_basic_broken.yaml"
    ]
    
    backup_files = list(backup_dir.glob("*"))
    backup_file_names = [f.name for f in backup_files]
    
    missing_backups = []
    for expected_file in expected_backup_files:
        if expected_file not in backup_file_names:
            missing_backups.append(expected_file)
    
    if missing_backups:
        print(f"   ❌ Missing backup files: {missing_backups}")
        return False
    else:
        print(f"   ✅ All {len(expected_backup_files)} files properly backed up")
        return True


def run_comprehensive_test():
    """Run all tests and provide summary."""
    print("🧪 COMPREHENSIVE CONSOLIDATION TESTING")
    print("=" * 60)
    
    # Run all tests
    import_results = test_imports()
    compatibility_result = test_backward_compatibility()
    functionality_result = test_functionality()
    file_results = test_missing_files()
    backup_result = test_backup_integrity()
    
    # Summary
    print("\n📊 TEST SUMMARY")
    print("=" * 60)
    
    total_tests = len(import_results) + 3  # imports + compatibility + functionality + backup
    passed_tests = sum(1 for result in import_results.values() if "✅" in result)
    passed_tests += (1 if compatibility_result else 0)
    passed_tests += (1 if functionality_result else 0)
    passed_tests += (1 if backup_result else 0)
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {passed_tests/total_tests*100:.1f}%")
    
    # Detailed results
    print("\n📋 DETAILED RESULTS:")
    
    print("\nImport Tests:")
    for module, result in import_results.items():
        print(f"  {module}: {result}")
    
    print(f"\nBackward Compatibility: {'✅ PASS' if compatibility_result else '❌ FAIL'}")
    print(f"Functionality: {'✅ PASS' if functionality_result else '❌ FAIL'}")
    print(f"Backup Integrity: {'✅ PASS' if backup_result else '❌ FAIL'}")
    
    # Recommendations
    print("\n💡 RECOMMENDATIONS:")
    
    if passed_tests == total_tests:
        print("✅ All tests passed! The consolidation is successful.")
        print("✅ You can now safely remove the old redundant files:")
        print("   - enhanced_cost_effectiveness.py")
        print("   - aggressive_cost_effectiveness_fix.py")
        print("   - enhanced_reporting.py")
        print("   - unified_reporting.py")
        print("   - consolidated_reporting_solution.py")
        print("   - improved_chart_generation.py")
        print("   - visualization_output_fix.py")
    else:
        print("❌ Some tests failed. Please review the issues above before proceeding.")
        print("❌ Do not remove the old files until all tests pass.")
    
    return passed_tests == total_tests


if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)
