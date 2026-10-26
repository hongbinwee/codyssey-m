const API = (window.APP_CONFIG?.API_BASE_URL || "http://localhost:8000").replace(/\/$/, "");
let currentConversationId = null;

const $ = (id) => document.getElementById(id);
const showToast = (text) => { const el=$("toast"); el.textContent=text; el.classList.add("show"); setTimeout(()=>el.classList.remove("show"),2200); };
const request = async (path, options={}) => {
  const { timeoutMs=60000, headers={}, ...fetchOptions } = options;
  const controller = new AbortController();
  const timer = setTimeout(()=>controller.abort(), timeoutMs);
  try {
    let res;
    try {
      res = await fetch(`${API}${path}`, { ...fetchOptions, headers:{"Content-Type":"application/json", ...headers}, signal:controller.signal });
    } catch(err) {
      if (err.name === "AbortError") throw new Error("서버 응답 시간이 초과되었습니다. 다시 시도해 주세요.");
      throw new Error("서버에 연결할 수 없습니다. 잠시 후 다시 시도해 주세요.");
    }
    if (!res.ok) {
      let detail="요청 실패";
      try {
        const body=await res.json();
        detail=Array.isArray(body.detail) ? body.detail.map(item=>item.msg).join(", ") : body.detail || detail;
      } catch {}
      throw new Error(detail);
    }
    return res.status === 204 ? null : res.json();
  } finally {
    clearTimeout(timer);
  }
};

const categoryKo = {study:"학습",project:"프로젝트",meeting:"회의",exercise:"운동",personal:"개인",other:"기타"};

async function loadSummary(){
  const s=await request("/api/data/summary");
  $("periodMetric").textContent=s.period ? `${s.period.start} ~ ${s.period.end}` : "데이터 없음";
  $("countMetric").textContent=`${s.count}개`;
  $("hoursMetric").textContent=`${s.metrics.total_hours}h`;
  $("weekdayMetric").textContent=s.busiest_weekday?.weekday || "-";
  $("categoryMetric").textContent=categoryKo[s.top_category?.category] || "-";
  const t=s.recent_trend;
  $("trendBadge").textContent=t.status === "no_data" ? "데이터 없음" : t.status === "increase" ? (t.change_percent === null ? "최근 증가 (비교 자료 없음)" : `최근 ↑ ${t.change_percent}%`) : t.status === "decrease" ? `최근 ↓ ${Math.abs(t.change_percent)}%` : "최근 유지";
  renderBars(s.weekday_distribution || {});
}

function renderBars(data){
  const order=["월요일","화요일","수요일","목요일","금요일","토요일","일요일"];
  const max=Math.max(1,...Object.values(data));
  $("bars").innerHTML=order.map(day=>`<div class="bar-wrap"><div class="bar" style="height:${Math.max(4,(data[day]||0)/max*90)}px"></div><span>${day[0]}</span></div>`).join("");
}

async function loadSchedules(){
  const rows=await request("/api/data");
  $("scheduleRows").innerHTML=rows.slice().reverse().map(row=>`<tr><td>${row.date}</td><td>${row.start_time}-${row.end_time}</td><td>${escapeHtml(row.title)}</td><td>${categoryKo[row.category]||row.category}</td><td><button data-delete="${row.id}">삭제</button></td></tr>`).join("");
  document.querySelectorAll("[data-delete]").forEach(btn=>btn.onclick=async()=>{
    if(!confirm("이 일정을 삭제할까요?")) return;
    btn.disabled=true; $("dataStatus").textContent="삭제 중...";
    try{
      await request(`/api/data/${btn.dataset.delete}`,{method:"DELETE"});
      await refreshAll();
      showToast("일정을 삭제했습니다.");
    }catch(err){showToast(`일정 삭제 실패: ${err.message}`);}
    finally{btn.disabled=false;$("dataStatus").textContent="";}
  });
}

async function loadConversations(){
  const rows=await request("/api/conversations");
  $("conversationList").innerHTML=rows.map(row=>`<div class="conversation-item" data-conversation="${row.id}"><strong>${escapeHtml(row.title)}</strong><small>${row.messages?.length||0} messages</small></div>`).join("") || "저장된 대화가 없습니다.";
  document.querySelectorAll("[data-conversation]").forEach(el=>el.onclick=()=>loadConversation(el.dataset.conversation));
}

async function loadConversation(id){
  try{
    const c=await request(`/api/conversations/${id}`); currentConversationId=id; $("messages").innerHTML=""; (c.messages||[]).forEach(m=>addMessage(m.role,m.content)); showToast("대화를 불러왔습니다.");
  }catch(err){showToast(`대화 불러오기 실패: ${err.message}`);}
}

function addMessage(role, content){
  const div=document.createElement("div"); div.className=`message ${role}`; div.textContent=content; $("messages").appendChild(div); $("messages").scrollTop=$("messages").scrollHeight;
}

function minutesBetween(start,end){ const [sh,sm]=start.split(":").map(Number); const [eh,em]=end.split(":").map(Number); return (eh*60+em)-(sh*60+sm); }
function escapeHtml(text){ const div=document.createElement("div"); div.textContent=text ?? ""; return div.innerHTML; }

$("scheduleForm").addEventListener("submit", async e=>{
  e.preventDefault(); const start=$("startTime").value,end=$("endTime").value,value=minutesBetween(start,end); if(value<=0){showToast("종료 시간이 시작 시간보다 늦어야 합니다.");return;}
  const payload={date:$("date").value,start_time:start,end_time:end,value,title:$("title").value,category:$("category").value,memo:$("memo").value||null};
  const submitButton=e.target.querySelector('button[type="submit"]');
  submitButton.disabled=true; $("dataStatus").textContent="저장 중...";
  try{
    await request("/api/data",{method:"POST",body:JSON.stringify(payload)});
    e.target.reset();
    await refreshAll();
    showToast("일정을 추가했습니다.");
  }catch(err){showToast(`일정 저장 실패: ${err.message}`);}
  finally{submitButton.disabled=false;$("dataStatus").textContent="";}
});

$("chatForm").addEventListener("submit", async e=>{
  e.preventDefault(); const text=$("chatInput").value.trim(); if(!text)return; addMessage("user",text); $("chatInput").value=""; $("chatStatus").textContent="AI가 분석 중..."; $("chatInput").disabled=true;
  try{ const result=await request("/api/chat",{method:"POST",body:JSON.stringify({message:text,conversation_id:currentConversationId})}); currentConversationId=result.conversation_id; addMessage("assistant",result.answer); await loadConversations(); }
  catch(err){ addMessage("assistant",`오류: ${err.message}`); }
  finally{$("chatStatus").textContent="대기 중";$("chatInput").disabled=false;$("chatInput").focus();}
});

async function refreshAll(){
  try{ await Promise.all([loadSummary(),loadSchedules(),loadConversations()]); }
  catch(err){ showToast(`연결 오류: ${err.message}`); }
}
$("refreshBtn").onclick=refreshAll;

$("exportBtn").onclick=async()=>{
  try{
    const rows=await request("/api/data");
    const blob=new Blob([JSON.stringify(rows,null,2)],{type:"application/json"});
    const url=URL.createObjectURL(blob);
    const a=document.createElement("a"); a.href=url; a.download=`myschedule-data-${new Date().toISOString().slice(0,10)}.json`; a.click(); URL.revokeObjectURL(url);
    showToast("일정 데이터를 내보냈습니다.");
  }catch(err){showToast(`내보내기 실패: ${err.message}`);}
};

const savedTheme=localStorage.getItem("theme");
if(savedTheme==="dark") document.body.classList.add("dark");
$("themeBtn").textContent=document.body.classList.contains("dark")?"라이트 모드":"다크 모드";
$("themeBtn").onclick=()=>{
  document.body.classList.toggle("dark");
  const dark=document.body.classList.contains("dark");
  localStorage.setItem("theme",dark?"dark":"light");
  $("themeBtn").textContent=dark?"라이트 모드":"다크 모드";
};

refreshAll();
