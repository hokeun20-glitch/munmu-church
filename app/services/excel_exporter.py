import io
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from datetime import datetime

def create_styled_workbook():
    wb = Workbook()
    ws = wb.active
    return wb, ws

def apply_header_style(cell, text):
    cell.value = text
    cell.font = Font(name="맑은 고딕", size=10, bold=True, color="FFFFFF")
    cell.fill = PatternFill(start_color="0F1D38", end_color="0F1D38", fill_type="solid")
    cell.alignment = Alignment(horizontal="center", vertical="center")

def apply_data_style(cell, text, align="center"):
    cell.value = text
    cell.font = Font(name="맑은 고딕", size=9)
    cell.alignment = Alignment(horizontal=align, vertical="center")

def export_event_registrations_to_excel(event_title: str, attendees: list) -> io.BytesIO:
    """행사 및 진중세례 신청자 명단을 공문서 수준의 엑셀 파일로 생성"""
    wb, ws = create_styled_workbook()
    ws.title = "참가자명단"

    # 1. 문서 제목
    ws.merge_cells("A1:H1")
    title_cell = ws["A1"]
    title_cell.value = f"[문무대교회] {event_title} 참가 접수 명부"
    title_cell.font = Font(name="맑은 고딕", size=14, bold=True, color="0F1D38")
    title_cell.alignment = Alignment(horizontal="left", vertical="center")
    ws.row_dimensions[1].height = 35

    # 2. 출력 일시
    ws.merge_cells("A2:H2")
    info_cell = ws["A2"]
    info_cell.value = f"출력일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 총 신청자 수: {len(attendees)}명"
    info_cell.font = Font(name="맑은 고딕", size=9, color="666666")
    ws.row_dimensions[2].height = 20

    # 3. 테이블 헤더
    headers = ["연번", "성명", "연락처", "소속", "계급/직분", "동반인원", "비고 (세례신청 등)", "신청일시"]
    for col_idx, header in enumerate(headers, start=1):
        cell = ws.cell(row=3, column=col_idx)
        apply_header_style(cell, header)
    ws.row_dimensions[3].height = 28

    # 4. 데이터 채우기
    thin_border = Border(
        left=Side(style='thin', color='DDDDDD'),
        right=Side(style='thin', color='DDDDDD'),
        top=Side(style='thin', color='DDDDDD'),
        bottom=Side(style='thin', color='DDDDDD')
    )

    for row_idx, item in enumerate(attendees, start=4):
        ws.row_dimensions[row_idx].height = 22
        row_data = [
            (row_idx - 3, "center"),
            (item.get("name", ""), "center"),
            (item.get("phone", ""), "center"),
            (item.get("affiliation", "-"), "left"),
            (item.get("rank_or_role", "-"), "center"),
            (f"+{item.get('companions_count', 0)}명", "center"),
            (item.get("memo", "-"), "left"),
            (str(item.get("created_at", "")), "center")
        ]
        for col_idx, (val, alignment) in enumerate(row_data, start=1):
            cell = ws.cell(row=row_idx, column=col_idx)
            apply_data_style(cell, val, align=alignment)
            cell.border = thin_border

    # 컬럼 너비 자동 설정
    widths = [8, 14, 18, 22, 14, 12, 30, 20]
    for idx, width in enumerate(widths, start=1):
        col_letter = chr(64 + idx)
        ws.column_dimensions[col_letter].width = width

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output

def export_consolations_to_excel(consolations: list) -> io.BytesIO:
    """위문 단체 및 위병소 출입 차량 목록 엑셀 생성"""
    wb, ws = create_styled_workbook()
    ws.title = "위문출입명부"

    ws.merge_cells("A1:H1")
    title_cell = ws["A1"]
    title_cell.value = "[문무대교회] 외부 위문 단체 방문 및 위병소 출입 차량 명부"
    title_cell.font = Font(name="맑은 고딕", size=14, bold=True, color="0F1D38")
    title_cell.alignment = Alignment(horizontal="left", vertical="center")
    ws.row_dimensions[1].height = 35

    headers = ["연번", "방문일자/시간", "신청단체명", "대표자(연락처)", "인원", "지원물품", "출입차량번호", "승인상태"]
    for col_idx, header in enumerate(headers, start=1):
        cell = ws.cell(row=3, column=col_idx)
        apply_header_style(cell, header)
    ws.row_dimensions[3].height = 28

    thin_border = Border(
        left=Side(style='thin', color='DDDDDD'),
        right=Side(style='thin', color='DDDDDD'),
        top=Side(style='thin', color='DDDDDD'),
        bottom=Side(style='thin', color='DDDDDD')
    )

    for row_idx, item in enumerate(consolations, start=4):
        ws.row_dimensions[row_idx].height = 24
        leader_info = f"{item.get('leader_name', '')} ({item.get('leader_phone', '')})"
        visit_dt = f"{item.get('visit_date', '')} {item.get('visit_time', '')}"
        row_data = [
            (row_idx - 3, "center"),
            (visit_dt, "center"),
            (item.get("group_name", ""), "left"),
            (leader_info, "center"),
            (f"{item.get('num_attendees', 0)}명", "center"),
            (item.get("items_summary", "-"), "left"),
            (item.get("vehicle_numbers", "-"), "left"),
            (item.get("status", ""), "center")
        ]
        for col_idx, (val, alignment) in enumerate(row_data, start=1):
            cell = ws.cell(row=row_idx, column=col_idx)
            apply_data_style(cell, val, align=alignment)
            cell.border = thin_border

    widths = [8, 22, 24, 22, 10, 30, 28, 14]
    for idx, width in enumerate(widths, start=1):
        col_letter = chr(64 + idx)
        ws.column_dimensions[col_letter].width = width

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output
