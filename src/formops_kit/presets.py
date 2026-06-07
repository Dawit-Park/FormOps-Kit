from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List


@dataclass(frozen=True)
class WorkflowPreset:
    slug: str
    label: str
    description: str
    config: Dict[str, Any]
    sample_csv: str


KR_COURSE_INQUIRY = WorkflowPreset(
    slug="kr-course-inquiry",
    label="강의/교육 문의",
    description="수강 신청, 강의 문의, 교육 상담 응답을 후속 처리 패킷으로 정리합니다.",
    config={
        "workflow_name": "강의 문의 접수",
        "folder_name_template": "{이름}-{관심 강의}",
        "required_fields": ["이름", "이메일", "관심 강의"],
        "templates": {
            "처리체크리스트.md": "# 강의 문의 처리: {이름}\n\n- [ ] 관심 강의 확인: {관심 강의}\n- [ ] 답장 보낼 이메일 확인: {이메일}\n- [ ] 희망 상담 시간 확인: {희망일} {희망시간}\n- [ ] 수강 목표 확인\n- [ ] 안내 자료 또는 다음 단계 준비\n\n## 수강 목표\n{목표}\n\n## 문의 내용\n{메시지}\n",
            "답장초안.md": "제목: {관심 강의} 문의 확인드립니다\n\n안녕하세요 {이름}님,\n\n{관심 강의} 문의 남겨주셔서 감사합니다. 남겨주신 목표는 다음과 같이 확인했습니다.\n\n{목표}\n\n희망하신 상담 시간은 {희망일} {희망시간}로 기록해두었습니다. 확인 후 커리큘럼과 다음 단계를 안내드리겠습니다.\n\n감사합니다.\n",
            "폴더계획.md": "# 폴더 구성안\n\n폴더명: {이름} - {관심 강의}\n\n추천 파일:\n- 문의내용.md\n- 수강목표.md\n- 상담메모.md\n- 안내자료/\n",
        },
        "calendar": {
            "enabled": True,
            "date_field": "희망일",
            "time_field": "희망시간",
            "duration_minutes": 30,
            "title_template": "강의 상담: {이름} / {관심 강의}",
            "description_template": "이메일: {이메일}\n목표: {목표}\n문의: {메시지}",
        },
    },
    sample_csv=(
        "접수일시,이름,이메일,문의 유형,희망일,희망시간,관심 강의,목표,메시지\n"
        "2026-06-07 09:00,샘플 수강생 A,learner-a@example.com,강의 문의,2026년 6월 12일,오후 2시,AI 업무 자동화,반복 업무를 줄이고 싶습니다,커리큘럼과 준비물을 알고 싶습니다\n"
        "2026-06-07 10:15,샘플 수강생 B,learner-b@example.com,수강 상담,2026.06.13,오전 10:30,노코드 자동화,팀 업무 접수 과정을 정리하고 싶습니다,수강 전 필요한 역량이 궁금합니다\n"
    ),
)


KR_CLIENT_CONSULTATION = WorkflowPreset(
    slug="kr-client-consultation",
    label="고객 상담/프로젝트 문의",
    description="고객 상담, 외주 문의, 프로젝트 검토 요청을 정리합니다.",
    config={
        "workflow_name": "고객 상담 접수",
        "folder_name_template": "{회사명}-{요청유형}",
        "required_fields": ["회사명", "담당자명", "이메일"],
        "templates": {
            "처리체크리스트.md": "# 상담 요청 처리: {회사명}\n\n- [ ] 요청 유형 확인: {요청유형}\n- [ ] 담당자 확인: {담당자명} / {이메일}\n- [ ] 희망 상담 시간 확인: {희망일} {희망시간}\n- [ ] 예산 범위 확인: {예산범위}\n- [ ] 사전 질문 준비\n\n## 현재 상황\n{상황}\n\n## 원하는 결과\n{목표}\n",
            "답장초안.md": "제목: {회사명} 상담 요청 확인드립니다\n\n안녕하세요 {담당자명}님,\n\n{요청유형} 관련 상담 요청 확인했습니다. 남겨주신 상황과 목표를 바탕으로 상담 전에 필요한 질문을 정리해두겠습니다.\n\n희망하신 시간은 {희망일} {희망시간}로 기록했습니다. 일정 확인 후 회신드리겠습니다.\n\n감사합니다.\n",
            "폴더계획.md": "# 폴더 구성안\n\n폴더명: {회사명} - {요청유형}\n\n추천 파일:\n- 접수내용.md\n- 사전질문.md\n- 회의메모.md\n- 제안서초안.md\n- 참고자료/\n",
        },
        "calendar": {
            "enabled": True,
            "date_field": "희망일",
            "time_field": "희망시간",
            "duration_minutes": 45,
            "title_template": "고객 상담: {회사명} / {요청유형}",
            "description_template": "담당자: {담당자명} <{이메일}>\n예산: {예산범위}\n상황: {상황}",
        },
    },
    sample_csv=(
        "접수일시,회사명,담당자명,이메일,요청유형,희망일,희망시간,예산범위,상황,목표\n"
        "2026-06-07 11:00,예시회사 A,샘플 담당자 A,contact-a@example.com,업무 자동화 상담,2026년 6월 15일,오후 3시,300만원 이하,폼 접수 후 수작업이 많습니다,접수 후속 처리를 표준화하고 싶습니다\n"
        "2026-06-07 13:20,예시회사 B,샘플 담당자 B,contact-b@example.com,운영 프로세스 정리,2026/06/16,14:30,500만원 이하,팀마다 처리 방식이 다릅니다,반복 가능한 체크리스트와 문서를 만들고 싶습니다\n"
    ),
)


KR_SETTLEMENT_REQUEST = WorkflowPreset(
    slug="kr-settlement-request",
    label="파트너 정산 요청",
    description="제휴, 파트너, 크리에이터 정산 요청을 검토용 파일로 정리합니다.",
    config={
        "workflow_name": "파트너 정산 요청",
        "folder_name_template": "{파트너명}-{정산월}",
        "required_fields": ["파트너명", "이메일", "정산월"],
        "templates": {
            "처리체크리스트.md": "# 정산 요청 처리: {파트너명}\n\n- [ ] 정산월 확인: {정산월}\n- [ ] 요청금액 확인: {요청금액}\n- [ ] 인보이스 링크 확인: {인보이스링크}\n- [ ] 지급 방식 확인: {지급방식}\n- [ ] 마감일 확인: {마감일}\n- [ ] 회신 보낼 이메일 확인: {이메일}\n\n## 메모\n{메모}\n",
            "답장초안.md": "제목: {정산월} 정산 요청 접수 확인드립니다\n\n안녕하세요 {파트너명}님,\n\n{정산월} 정산 요청을 확인했습니다. 요청금액은 {요청금액}, 지급 방식은 {지급방식}로 기록했습니다.\n\n인보이스와 정산 정보를 검토한 뒤 누락 사항이 있으면 회신드리겠습니다.\n\n감사합니다.\n",
            "폴더계획.md": "# 폴더 구성안\n\n폴더명: {파트너명} - {정산월}\n\n추천 파일:\n- 정산요청.md\n- 인보이스.pdf\n- 검토메모.md\n- 지급기록.md\n",
        },
        "calendar": {
            "enabled": True,
            "date_field": "마감일",
            "duration_minutes": 30,
            "title_template": "정산 마감: {파트너명} / {정산월}",
            "description_template": "이메일: {이메일}\n금액: {요청금액}\n인보이스: {인보이스링크}",
        },
    },
    sample_csv=(
        "접수일시,파트너명,이메일,정산월,요청금액,인보이스링크,지급방식,마감일,메모\n"
        "2026-06-07 15:00,예시 파트너 A,partner-a@example.com,2026년 5월,820000원,https://example.com/invoice-a,계좌이체,2026년 6월 20일,캠페인 A 정산 요청입니다\n"
        "2026-06-07 16:30,예시 파트너 B,partner-b@example.com,2026년 5월,460000원,https://example.com/invoice-b,계좌이체,2026.06.21,인보이스 확인 부탁드립니다\n"
    ),
)


PRESETS = (
    KR_COURSE_INQUIRY,
    KR_CLIENT_CONSULTATION,
    KR_SETTLEMENT_REQUEST,
)


def list_presets() -> List[WorkflowPreset]:
    return list(PRESETS)


def default_preset() -> WorkflowPreset:
    return KR_COURSE_INQUIRY


def get_preset(slug: str) -> WorkflowPreset:
    for preset in PRESETS:
        if preset.slug == slug:
            return preset
    available = ", ".join(preset.slug for preset in PRESETS)
    raise ValueError(f"Unknown preset '{slug}'. Available presets: {available}")


def write_preset_files(preset_slug: str, target_dir: Path) -> Dict[str, Path]:
    preset = get_preset(preset_slug)
    target_dir.mkdir(parents=True, exist_ok=True)
    config_path = target_dir / "config.json"
    csv_path = target_dir / "responses.csv"
    config_path.write_text(json.dumps(preset.config, indent=2, ensure_ascii=False), encoding="utf-8")
    csv_path.write_text(preset.sample_csv, encoding="utf-8-sig")
    return {"config": config_path, "csv": csv_path}
