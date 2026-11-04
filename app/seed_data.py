from app.database import get_db, init_db
from datetime import datetime, timedelta

def seed():
    init_db()
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 1. 설교 영상
        cursor.execute("SELECT COUNT(*) FROM sermons")
        if cursor.fetchone()[0] == 0:
            sermons_data = [
                (
                    "청년의 때에 여호와를 기억하라",
                    "김요한 군종목사",
                    "2026-11-01",
                    "전도서 12장 1-2절",
                    "W5qM9uA_g28", # 대체 가능한 실존 기독교/찬양 ID
                    "군 복무와 훈련의 광야 속에서 흔들리지 않는 영적 나침반을 세우는 청년 장교의 사명",
                    428
                ),
                (
                    "강하고 담대하라 두려워하지 말며 놀라지 말라",
                    "김요한 군종목사",
                    "2026-10-25",
                    "여호수아 1장 7-9절",
                    "8p2z1L4zZ_0",
                    "야전 소대장으로서 수많은 부하를 이끌기 전, 하나님 앞에서 무릎 꿇는 진정한 영적 리더십",
                    612
                ),
                (
                    "십자가 군병들아, 주의 군기 들고",
                    "이진우 초청목사 (전 한국군종목사단장)",
                    "2026-10-18",
                    "디모데후서 2장 1-4절",
                    "kJQP7kiw5Fk",
                    "청년 장교 복음화와 대한민국 안보를 위해 헌신하는 그리스도의 좋은 군사",
                    850
                )
            ]
            cursor.executemany("""
                INSERT INTO sermons (title, preacher, date, scripture, youtube_id, description, views)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, sermons_data)

        # 2. 주보
        cursor.execute("SELECT COUNT(*) FROM bulletins")
        if cursor.fetchone()[0] == 0:
            bulletins_data = [
                (
                    "2026년 11월 첫째 주일 문무대 주보 (제24-44호)",
                    "2026-11-01",
                    "제2026-44호",
                    "https://images.unsplash.com/photo-1544717305-2782549b5136?auto=format&fit=crop&w=1200&q=80",
                    "#"
                ),
                (
                    "2026년 10월 넷째 주일 문무대 주보 (제24-43호)",
                    "2026-10-25",
                    "제2026-43호",
                    "https://images.unsplash.com/photo-1455390582262-044cdead277a?auto=format&fit=crop&w=1200&q=80",
                    "#"
                )
            ]
            cursor.executemany("""
                INSERT INTO bulletins (title, date, volume_no, image_url, pdf_url)
                VALUES (?, ?, ?, ?, ?)
            """, bulletins_data)

        # 3. 상담 슬롯 (향후 14일간)
        cursor.execute("SELECT COUNT(*) FROM counseling_slots")
        if cursor.fetchone()[0] == 0:
            slots_data = []
            today = datetime.now()
            time_choices = ["10:00 - 11:00 (오전)", "14:00 - 15:00 (오후)", "16:00 - 17:00 (오후)", "19:30 - 20:30 (야간)"]
            for i in range(1, 15):
                slot_date = (today + timedelta(days=i)).strftime("%Y-%m-%d")
                # 토요일/주일 제외한 평일 위주 슬롯 생성
                day_of_week = (today + timedelta(days=i)).weekday()
                if day_of_week in [0, 1, 2, 3, 4]: # 월~금
                    for t in time_choices:
                        slots_data.append((slot_date, t, 1, "김요한 군종목사"))
            cursor.executemany("""
                INSERT INTO counseling_slots (date, time_slot, is_available, counselor_name)
                VALUES (?, ?, ?, ?)
            """, slots_data)

        # 4. 정기 및 특별 행사
        cursor.execute("SELECT COUNT(*) FROM events")
        if cursor.fetchone()[0] == 0:
            events_data = [
                (
                    "2026 하계 ROTC 후보생 진중세례 및 성찬예배",
                    "진중세례",
                    "2026-11-22",
                    "주일 오후 14:00",
                    "문무대교회 본당 대예배실",
                    300,
                    184,
                    "https://images.unsplash.com/photo-1438232992991-995b7058bbb3?auto=format&fit=crop&w=1200&q=80",
                    "육군학생군사학교 하계 입영훈련 중 하나님의 자녀로 거듭나는 거룩한 진중세례식입니다. 군선교 후원교회 목회자 및 성도 여러분의 기도와 격려를 부탁드립니다.",
                    1
                ),
                (
                    "문무대 찬양의 밤 및 청년장교 영성캠프",
                    "특별영성집회",
                    "2026-11-15",
                    "주일 저녁 18:30",
                    "문무대교회 비전홀",
                    150,
                    95,
                    "https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?auto=format&fit=crop&w=1200&q=80",
                    "뜨거운 찬양과 기도로 군 복무의 두려움을 이기고 영적 전신갑주를 입는 청년 장교 찬양의 밤입니다.",
                    1
                ),
                (
                    "전국 학군단 기독동문회(ROTC 기독장교연합) 초청 위문예배",
                    "동문연합",
                    "2026-12-06",
                    "주일 오전 10:30",
                    "문무대교회 본당 대예배실",
                    250,
                    120,
                    "https://images.unsplash.com/photo-1519491050282-cf00c82424b4?auto=format&fit=crop&w=1200&q=80",
                    "선배 기독 장교들이 문무대를 찾아 후배 후보생들을 위문하고 신앙의 대를 잇는 따뜻한 연합예배입니다.",
                    1
                )
            ]
            cursor.executemany("""
                INSERT INTO events (title, category, date, time, location, max_participants, current_participants, image_url, description, is_open)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, events_data)

        # 5. 위문 신청 샘플 (일정 중복 방지 테스트용)
        cursor.execute("SELECT COUNT(*) FROM consolation_requests")
        if cursor.fetchone()[0] == 0:
            consolations_data = [
                (
                    "서울 영락교회 청년선교부",
                    "박준형 목사",
                    "010-3321-4455",
                    "mission@youngnak.org",
                    "2026-11-15",
                    "오후 13:00 - 16:00",
                    25,
                    "수제 햄버거 세트 400개, 보온 텀블러, 청년 신앙도서",
                    "12가3456, 34나7890 (버스 1대, 승용차 1대)",
                    "하계 입영훈련 후보생 위문 및 간식 전달, 주일 2부 예배 특송",
                    "승인완료",
                    "위병소 출입 조치 완료 / 본당 친교실 사용 배정"
                ),
                (
                    "한국기독실업인회(CBMC) 충북지회",
                    "최영식 장로",
                    "010-8877-6655",
                    "cbmc_cb@gmail.com",
                    "2026-11-22",
                    "오전 10:00 - 13:00",
                    15,
                    "고급 간식 박스 500세트 및 장학후원금 전달",
                    "56다9988 외 승용차 3대",
                    "진중세례식 축하 및 후보생 격려 방문",
                    "승인완료",
                    "세례식 순서지 협의 완료"
                )
            ]
            cursor.executemany("""
                INSERT INTO consolation_requests (group_name, leader_name, leader_phone, leader_email, visit_date, visit_time, num_attendees, items_summary, vehicle_numbers, purpose, status, admin_memo)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, consolations_data)

        # 6. 교회 연혁
        cursor.execute("SELECT COUNT(*) FROM history_events")
        if cursor.fetchone()[0] == 0:
            history_data = [
                (
                    "1985",
                    "03월",
                    "학생중앙군사학교 군종 사역 태동 (성남 시대)",
                    "경기도 성남 학생중앙군사학교 창설과 함께 장교 후보생들을 향한 영적 돌봄과 군종선교 사역의 첫발을 내디뎠습니다.",
                    "https://images.unsplash.com/photo-1548625361-195fe5795df5?auto=format&fit=crop&w=800&q=80"
                ),
                (
                    "1995",
                    "07월",
                    "ROTC 기독장교 연합 선교대회 및 진중세례 사역 정착",
                    "전국 대학교 학군사관후보생들의 입영훈련 기간 중 대규모 진중세례식을 정례화하여 매년 수천 명의 기독 장교를 배출하기 시작했습니다.",
                    "https://images.unsplash.com/photo-1438232992991-995b7058bbb3?auto=format&fit=crop&w=800&q=80"
                ),
                (
                    "2011",
                    "11월",
                    "충북 괴산 신축 캠퍼스 이전 및 문무대교회 대성전 헌당",
                    "국방개혁에 따라 학교가 괴산으로 전면 이전하며, 1,200석 규모의 현대식 대예배실, 비전센터, 세례탕을 갖춘 웅장한 대성전을 하나님의 은혜로 헌당하였습니다.",
                    "https://images.unsplash.com/photo-1478147427282-58a87a120781?auto=format&fit=crop&w=800&q=80"
                ),
                (
                    "2012",
                    "01월",
                    "육군학생군사학교로 부대 명칭 개편 및 선교 비전 선포",
                    "'청년 장교의 가슴마다 그리스도를!'이라는 비전 표어를 선포하고, 장교 후보생뿐 아니라 기간병, 군인가족을 아우르는 복음의 요람으로 우뚝 섰습니다.",
                    "https://images.unsplash.com/photo-1519491050282-cf00c82424b4?auto=format&fit=crop&w=800&q=80"
                ),
                (
                    "2020",
                    "08월",
                    "스마트 군선교 인프라 및 상담 핫라인 구축",
                    "팬데믹과 병영 환경 변화에 발맞추어 고화질 온라인 예배 송출 시스템과 후보생 비대면 상담 핫라인을 선제적으로 개통하였습니다.",
                    "https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?auto=format&fit=crop&w=800&q=80"
                ),
                (
                    "2026",
                    "현재",
                    "조국 수호와 복음화의 중심, 다음 세대 리더 양성",
                    "매년 육군 소위 임관자의 약 90%가 거쳐 가는 육군학생군사학교에서, 하나님을 경외하고 나라를 사랑하는 참된 군인 리더들을 길러내고 있습니다.",
                    "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=800&q=80"
                )
            ]
            cursor.executemany("""
                INSERT INTO history_events (year, month, title, description, image_url)
                VALUES (?, ?, ?, ?, ?)
            """, history_data)

        # 7. 갤러리 (사진)
        cursor.execute("SELECT COUNT(*) FROM gallery_items")
        if cursor.fetchone()[0] == 0:
            gallery_data = [
                (
                    "문무대교회 대성전 전경 (1,200석 규모)",
                    "시설전경",
                    "https://images.unsplash.com/photo-1548625361-195fe5795df5?auto=format&fit=crop&w=1200&q=80",
                    "2026-10-15",
                    "괴산 문무대 영내에 웅장하게 자리 잡은 대성전 전경. 최첨단 음향과 영상 설비를 갖추고 있습니다."
                ),
                (
                    "하계 입영훈련 훈련생 진중세례식 현장",
                    "진중세례",
                    "https://images.unsplash.com/photo-1438232992991-995b7058bbb3?auto=format&fit=crop&w=1200&q=80",
                    "2026-08-20",
                    "고된 훈련 중 예수 그리스도를 구주로 영접하고 세례를 받는 후보생들의 뜨거운 눈물과 환희."
                ),
                (
                    "주일 2부 ROTC 후보생 찬양 연합예배",
                    "주일예배",
                    "https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?auto=format&fit=crop&w=1200&q=80",
                    "2026-10-25",
                    "주일 아침 대성전을 가득 메운 장교 후보생들의 우렁찬 찬양과 기도."
                ),
                (
                    "야외 십자가 동산 및 기도 산책로",
                    "시설전경",
                    "https://images.unsplash.com/photo-1519491050282-cf00c82424b4?auto=format&fit=crop&w=1200&q=80",
                    "2026-09-10",
                    "사색과 묵상을 위해 성전 뒤편에 조성된 고요한 십자가 기도 동산입니다."
                ),
                (
                    "외부 후원교회 및 선교단 위문 행사",
                    "위문교제",
                    "https://images.unsplash.com/photo-1529156069898-49953e39b3ac?auto=format&fit=crop&w=1200&q=80",
                    "2026-10-11",
                    "어머니의 마음으로 준비해 주신 따뜻한 간식과 사랑으로 후보생들을 위로하는 자리."
                ),
                (
                    "문무대교회 친교실 및 만남의 카페",
                    "시설전경",
                    "https://images.unsplash.com/photo-1442512595331-e89e73853f31?auto=format&fit=crop&w=1200&q=80",
                    "2026-10-01",
                    "예배 후 교역자, 장병, 가족들이 따뜻한 차와 교제를 나누는 열린 공간."
                )
            ]
            cursor.executemany("""
                INSERT INTO gallery_items (title, category, image_url, date, description)
                VALUES (?, ?, ?, ?, ?)
            """, gallery_data)

        # 8. 교역자 프로필
        cursor.execute("SELECT COUNT(*) FROM pastors")
        if cursor.fetchone()[0] == 0:
            pastors_data = [
                (
                    "김요한",
                    "담임 군종목사 / 소령(진)",
                    "설교 총괄, 목회 및 후보생 영성 지도",
                    "총신대학교 신학대학원(M.Div.)을 졸업하고 대한예수교장로회(합동) 군종목사로 임관하여 전후방 야전부대를 거쳐 현재 육군학생군사학교 문무대교회 담임으로 섬기고 있습니다. 청년 장교들이 복음의 능력을 힘입어 야전으로 나아가도록 돕는 것이 평생의 사명입니다.",
                    "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=600&q=80",
                    "“너는 청년의 때에 너의 창조주를 기억하라” (전 12:1)"
                ),
                (
                    "박사랑",
                    "교육전도사",
                    "청년부 사역, 찬양팀 지도 및 상담 코디네이터",
                    "장로회신학대학교 신학과를 졸업하고 군선교의 부르심을 받아 문무대교회 청년 찬양팀과 훈련생 상담 지원을 전담하고 있습니다. 지친 후보생들의 눈높이에서 따뜻한 위로와 기도로 동행합니다.",
                    "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=600&q=80",
                    "“여호와는 나의 목자시니 내게 부족함이 없으리로다” (시 23:1)"
                ),
                (
                    "이믿음",
                    "수석 군종병 / 병장",
                    "예배 미디어, 방송 시스템 및 시설 관리",
                    "문무대교회의 주일예배 방송, 영상 송출, 스마트 주보 제작 및 성도/후보생 안내를 담당하고 있습니다.",
                    "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=600&q=80",
                    "“내게 능력 주시는 자 안에서 내가 모든 것을 할 수 있느니라” (빌 4:13)"
                )
            ]
            cursor.executemany("""
                INSERT INTO pastors (name, title, role, bio, image_url, scripture)
                VALUES (?, ?, ?, ?, ?, ?)
            """, pastors_data)

        # 9. 훈련생 응원 편지 샘플
        cursor.execute("SELECT COUNT(*) FROM support_letters")
        if cursor.fetchone()[0] == 0:
            letters_data = [
                (
                    "김민석 후보생 (ROTC 64기)",
                    "교육여단 2대대 3중대",
                    "어머니 이혜숙",
                    "가족",
                    "사랑하는 아들 민석아! 무더위 속에서도 묵묵히 훈련받고 있을 네 모습을 떠올리며 매일 새벽 문무대교회를 향해 기도한단다. 하나님께서 너의 발걸음을 지키시고 강한 장교로 세워주실 줄 믿는다. 건강하게 첫 휴가 때 보자!",
                    0
                ),
                (
                    "박준서 후보생 (학사사관 71기)",
                    "교육여단 1대대 1중대",
                    "고려대 기독학생회 동기 일동",
                    "친구/선후배",
                    "준서야! 캠퍼스에서 함께 기도하던 때가 엊그제 같은데 어느덧 훈련의 반을 지나고 있네! 주일예배 때 문무대교회에서 은혜 많이 받고, 야전의 빛과 소금이 되는 멋진 소대장이 되길 늘 응원한다!",
                    0
                )
            ]
            cursor.executemany("""
                INSERT INTO support_letters (recipient_name, recipient_unit, sender_name, sender_relation, content, is_private)
                VALUES (?, ?, ?, ?, ?, ?)
            """, letters_data)
            
        conn.commit()

if __name__ == "__main__":
    seed()
    print("Seed data loaded successfully.")
