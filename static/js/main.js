// 문무대교회 공통 프론트엔드 유틸리티
document.addEventListener("DOMContentLoaded", () => {
    // 모바일 햄버거 메뉴 토글
    const mobileBtn = document.getElementById("mobile-menu-btn");
    const mobileMenu = document.getElementById("mobile-menu");
    if (mobileBtn && mobileMenu) {
        mobileBtn.addEventListener("click", () => {
            mobileMenu.classList.toggle("hidden");
        });
    }

    // 네비게이션 스크롤 스타일링
    const navbar = document.getElementById("main-nav");
    if (navbar) {
        window.addEventListener("scroll", () => {
            if (window.scrollY > 40) {
                navbar.classList.add("bg-white/95", "shadow-md", "backdrop-blur-md");
                navbar.classList.remove("bg-white/90");
            } else {
                navbar.classList.add("bg-white/90");
                navbar.classList.remove("shadow-md");
            }
        });
    }
});

// 토스트 메시지 시스템
function showToast(message, type = "info") {
    let container = document.getElementById("toast-container");
    if (!container) {
        container = document.createElement("div");
        container.id = "toast-container";
        document.body.appendChild(container);
    }

    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    
    let icon = "fa-info-circle text-blue-400";
    if (type === "success") icon = "fa-check-circle text-emerald-400";
    if (type === "error") icon = "fa-exclamation-circle text-rose-400";

    toast.innerHTML = `
        <i class="fa-solid ${icon} text-lg"></i>
        <div class="flex-1">${message}</div>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = "0";
        toast.style.transform = "translateX(100%)";
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// 계좌번호 원클릭 복사
function copyAccount(accountNumber, bankName) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(accountNumber).then(() => {
            showToast(`${bankName} 계좌번호(${accountNumber})가 클립보드에 복사되었습니다.`, "success");
        }).catch(() => {
            fallbackCopy(accountNumber, bankName);
        });
    } else {
        fallbackCopy(accountNumber, bankName);
    }
}

function fallbackCopy(text, bankName) {
    const textarea = document.createElement("textarea");
    textarea.value = text;
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand("copy");
    document.body.removeChild(textarea);
    showToast(`${bankName} 계좌번호가 복사되었습니다.`, "success");
}

// ics 캘린더 파일 다운로드 생성기
function downloadIcsFile(title, dateStr, timeStr, details, location = "육군학생군사학교 문무대교회 목양실") {
    try {
        const parts = timeStr.split("-");
        const startPart = parts[0].trim().replace("오전", "").replace("오후", "").replace("야간", "").trim();
        const endPart = parts[1] ? parts[1].split("(")[0].trim() : startPart;

        const startClean = dateStr.replace(/-/g, "") + "T" + startPart.replace(":", "") + "00";
        const endClean = dateStr.replace(/-/g, "") + "T" + endPart.replace(":", "") + "00";

        const icsData = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//Munmu Church//Counseling System//KO",
            "BEGIN:VEVENT",
            `SUMMARY:${title}`,
            `DESCRIPTION:${details.replace(/\n/g, "\\n")}`,
            `LOCATION:${location}`,
            `DTSTART:${startClean}`,
            `DTEND:${endClean}`,
            "STATUS:CONFIRMED",
            "END:VEVENT",
            "END:VCALENDAR"
        ].join("\r\n");

        const blob = new Blob([icsData], { type: "text/calendar;charset=utf-8" });
        const link = document.createElement("a");
        link.href = window.URL.createObjectURL(blob);
        link.setAttribute("download", `문무대교회_상담일정_${dateStr}.ics`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    } catch (e) {
        console.error("ICS generation error:", e);
    }
}
