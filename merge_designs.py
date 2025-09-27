#!/usr/bin/env python3
"""
디자인 파일 병합 도구
여러 design*.json 파일을 안전하게 병합하여 최종 design.json을 생성합니다.
"""

import json
import os
from pathlib import Path

def merge_design_files():
    """여러 디자인 파일을 병합하여 최종 design.json을 생성"""
    
    # 디자인 파일들이 있는 디렉토리
    design_dir = Path("my-project")
    
    # 병합할 디자인 파일들 (우선순위 순서)
    design_files = [
        "design.json",      # 기본 디자인 (최우선)
        "design2.json",     # 추가 디자인 1
        "design3.json",     # 추가 디자인 2
        # 필요에 따라 더 추가 가능
    ]
    
    # 최종 병합된 디자인
    merged_design = {
        "designSystem": {
            "componentStyles": {}
        }
    }
    
    print("🎨 디자인 파일 병합 시작...")
    
    for design_file in design_files:
        file_path = design_dir / design_file
        
        if file_path.exists():
            print(f"📁 {design_file} 파일 발견 - 병합 중...")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    design_data = json.load(f)
                
                # 디자인 시스템 병합
                if "designSystem" in design_data:
                    if "componentStyles" in design_data["designSystem"]:
                        # 기존 스타일과 새 스타일 병합 (새 스타일이 우선)
                        merged_design["designSystem"]["componentStyles"].update(
                            design_data["designSystem"]["componentStyles"]
                        )
                        print(f"✅ {design_file} 병합 완료")
                    else:
                        print(f"⚠️  {design_file}에 componentStyles가 없습니다")
                else:
                    print(f"⚠️  {design_file}에 designSystem이 없습니다")
                    
            except json.JSONDecodeError as e:
                print(f"❌ {design_file} JSON 파싱 오류: {e}")
            except Exception as e:
                print(f"❌ {design_file} 처리 중 오류: {e}")
        else:
            print(f"ℹ️  {design_file} 파일이 없습니다 - 건너뜀")
    
    # 병합된 결과를 design.json에 저장
    output_path = design_dir / "design.json"
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(merged_design, f, indent=2, ensure_ascii=False)
        print(f"🎉 최종 design.json 생성 완료: {output_path}")
        
        # 병합된 디자인 정보 출력
        print("\n📊 병합된 디자인 구성요소:")
        for component, styles in merged_design["designSystem"]["componentStyles"].items():
            print(f"  - {component}: {len(styles)}개 속성")
            
    except Exception as e:
        print(f"❌ 최종 파일 저장 중 오류: {e}")

def create_sample_design2():
    """샘플 design2.json 파일 생성"""
    sample_design2 = {
        "designSystem": {
            "componentStyles": {
                "modals": {
                    "background": "#FFFFFF",
                    "overlay": "rgba(0, 0, 0, 0.5)",
                    "border": "#E5E7EB",
                    "radius": "8px",
                    "shadow": "0px 4px 12px rgba(0,0,0,0.15)"
                },
                "alerts": {
                    "success": {"bg": "#D1FAE5", "text": "#065F46", "border": "#A7F3D0"},
                    "warning": {"bg": "#FEF3C7", "text": "#92400E", "border": "#FCD34D"},
                    "error": {"bg": "#FEE2E2", "text": "#991B1B", "border": "#FCA5A5"},
                    "info": {"bg": "#DBEAFE", "text": "#1E40AF", "border": "#93C5FD"}
                },
                "forms": {
                    "input": {
                        "background": "#FFFFFF",
                        "border": "#D1D5DB",
                        "borderFocus": "#4F46E5",
                        "radius": "6px",
                        "padding": "8px 12px"
                    },
                    "label": {
                        "color": "#374151",
                        "fontWeight": "500",
                        "marginBottom": "4px"
                    }
                }
            }
        }
    }
    
    design2_path = Path("my-project/design2.json")
    try:
        with open(design2_path, 'w', encoding='utf-8') as f:
            json.dump(sample_design2, f, indent=2, ensure_ascii=False)
        print(f"📝 샘플 design2.json 생성 완료: {design2_path}")
    except Exception as e:
        print(f"❌ design2.json 생성 중 오류: {e}")

if __name__ == "__main__":
    print("🚀 WBS 프로젝트 디자인 병합 도구")
    print("=" * 50)
    
    # 샘플 design2.json 생성 (이미 있으면 건너뜀)
    if not Path("my-project/design2.json").exists():
        create_sample_design2()
    
    # 디자인 파일들 병합
    merge_design_files()
    
    print("\n✨ 병합 완료! 이제 CSS 파일을 업데이트하세요.")
    print("💡 CSS 업데이트 명령: python update_css.py")

