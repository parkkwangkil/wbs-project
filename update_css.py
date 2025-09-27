#!/usr/bin/env python3
"""
CSS 업데이트 도구
design.json 파일을 기반으로 design-system.css를 자동 업데이트합니다.
"""

import json
import re
from pathlib import Path

def update_css_from_design():
    """design.json을 기반으로 CSS 파일을 업데이트"""
    
    design_path = Path("my-project/design.json")
    css_path = Path("static/css/design-system.css")
    
    if not design_path.exists():
        print("❌ design.json 파일을 찾을 수 없습니다.")
        return
    
    try:
        # design.json 읽기
        with open(design_path, 'r', encoding='utf-8') as f:
            design_data = json.load(f)
        
        print("🎨 design.json 파일 로드 완료")
        
        # CSS 변수 생성
        css_variables = generate_css_variables(design_data)
        
        # 기존 CSS 파일 읽기
        if css_path.exists():
            with open(css_path, 'r', encoding='utf-8') as f:
                existing_css = f.read()
        else:
            existing_css = ""
        
        # CSS 변수 섹션 업데이트
        updated_css = update_css_variables_section(existing_css, css_variables)
        
        # CSS 파일 저장
        with open(css_path, 'w', encoding='utf-8') as f:
            f.write(updated_css)
        
        print(f"✅ CSS 파일 업데이트 완료: {css_path}")
        
    except Exception as e:
        print(f"❌ CSS 업데이트 중 오류: {e}")

def generate_css_variables(design_data):
    """디자인 데이터에서 CSS 변수 생성"""
    
    variables = []
    variables.append("/* WBS Project - Design System based on provided JSON */")
    variables.append("")
    variables.append("/* CSS Variables based on design.json */")
    variables.append(":root {")
    
    if "designSystem" in design_data and "componentStyles" in design_data["designSystem"]:
        component_styles = design_data["designSystem"]["componentStyles"]
        
        for component, styles in component_styles.items():
            if component == "sidebar":
                variables.append("  /* Sidebar Colors */")
                for key, value in styles.items():
                    css_var = f"  --sidebar-{key.replace('Color', '').replace('Background', '')}: {value};"
                    variables.append(css_var)
                variables.append("")
                
            elif component == "cards":
                variables.append("  /* Card Colors */")
                for key, value in styles.items():
                    css_var = f"  --card-{key.replace('Color', '').replace('surface', 'surface')}: {value};"
                    variables.append(css_var)
                variables.append("")
                
            elif component == "buttons":
                variables.append("  /* Button Colors */")
                for button_type, button_styles in styles.items():
                    for state, state_styles in button_styles.items():
                        for prop, value in state_styles.items():
                            css_var = f"  --btn-{button_type}-{state}-{prop}: {value};"
                            variables.append(css_var)
                variables.append("")
                
            elif component == "statusBadges":
                variables.append("  /* Status Badge Colors */")
                for status, status_styles in styles.items():
                    for prop, value in status_styles.items():
                        css_var = f"  --status-{status}-{prop}: {value};"
                        variables.append(css_var)
                variables.append("")
                
            elif component == "typography":
                variables.append("  /* Typography Colors */")
                for key, value in styles.items():
                    css_var = f"  --text-{key}: {value};"
                    variables.append(css_var)
                variables.append("")
                
            elif component == "modals":
                variables.append("  /* Modal Colors */")
                for key, value in styles.items():
                    css_var = f"  --modal-{key}: {value};"
                    variables.append(css_var)
                variables.append("")
                
            elif component == "alerts":
                variables.append("  /* Alert Colors */")
                for alert_type, alert_styles in styles.items():
                    for prop, value in alert_styles.items():
                        css_var = f"  --alert-{alert_type}-{prop}: {value};"
                        variables.append(css_var)
                variables.append("")
                
            elif component == "forms":
                variables.append("  /* Form Colors */")
                for form_element, form_styles in styles.items():
                    if isinstance(form_styles, dict):
                        for prop, value in form_styles.items():
                            css_var = f"  --form-{form_element}-{prop}: {value};"
                            variables.append(css_var)
                    else:
                        css_var = f"  --form-{form_element}: {form_styles};"
                        variables.append(css_var)
                variables.append("")
                
            elif component == "projectStats":
                variables.append("  /* Project Stats Colors */")
                for stat_element, stat_styles in styles.items():
                    if isinstance(stat_styles, dict):
                        for prop, value in stat_styles.items():
                            css_var = f"  --project-stats-{stat_element}-{prop}: {value};"
                            variables.append(css_var)
                    else:
                        css_var = f"  --project-stats-{stat_element}: {stat_styles};"
                        variables.append(css_var)
                variables.append("")
                
            elif component == "adSidebar":
                variables.append("  /* Ad Sidebar Colors */")
                for ad_element, ad_styles in styles.items():
                    if isinstance(ad_styles, dict):
                        for prop, value in ad_styles.items():
                            css_var = f"  --ad-sidebar-{ad_element}-{prop}: {value};"
                            variables.append(css_var)
                    else:
                        css_var = f"  --ad-sidebar-{ad_element}: {ad_styles};"
                        variables.append(css_var)
                variables.append("")
                
            elif component == "appShell":
                variables.append("  /* App Shell Colors */")
                for shell_element, shell_styles in styles.items():
                    if isinstance(shell_styles, dict):
                        for prop, value in shell_styles.items():
                            css_var = f"  --app-shell-{shell_element}-{prop}: {value};"
                            variables.append(css_var)
                    else:
                        css_var = f"  --app-shell-{shell_element}: {shell_styles};"
                        variables.append(css_var)
                variables.append("")
                
            elif component == "topbar":
                variables.append("  /* Topbar Colors */")
                for topbar_element, topbar_styles in styles.items():
                    if isinstance(topbar_styles, dict):
                        for prop, value in topbar_styles.items():
                            css_var = f"  --topbar-{topbar_element}-{prop}: {value};"
                            variables.append(css_var)
                    else:
                        css_var = f"  --topbar-{topbar_element}: {topbar_styles};"
                        variables.append(css_var)
                variables.append("")
    
    variables.append("  /* Background Colors */")
    variables.append("  --bg-surface: #F9FAFB;")
    variables.append("  --bg-primary: #FFFFFF;")
    variables.append("}")
    variables.append("")
    
    return "\n".join(variables)

def update_css_variables_section(existing_css, new_variables):
    """기존 CSS에서 변수 섹션을 업데이트"""
    
    # CSS 변수 섹션 찾기 (/* CSS Variables based on design.json */ 부터 :root { ... } 까지)
    pattern = r'/\* CSS Variables based on design\.json \*/.*?^}'
    
    if re.search(pattern, existing_css, re.MULTILINE | re.DOTALL):
        # 기존 변수 섹션 교체
        updated_css = re.sub(pattern, new_variables, existing_css, flags=re.MULTILINE | re.DOTALL)
    else:
        # 기존 CSS가 없거나 변수 섹션이 없으면 새로 추가
        if existing_css.strip():
            updated_css = new_variables + "\n\n" + existing_css
        else:
            updated_css = new_variables
    
    return updated_css

if __name__ == "__main__":
    print("🎨 WBS 프로젝트 CSS 업데이트 도구")
    print("=" * 40)
    
    update_css_from_design()
    
    print("\n✨ CSS 업데이트 완료!")
    print("💡 이제 Django 서버를 재시작하여 변경사항을 확인하세요.")
