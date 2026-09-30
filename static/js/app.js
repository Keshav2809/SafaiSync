function getCookie(name){
 let cookieValue=null;
 if(document.cookie && document.cookie!==""){
  document.cookie.split(";").forEach(c=>{
   c=c.trim();
   if(c.startsWith(name+"=")) cookieValue=decodeURIComponent(c.slice(name.length+1));
  });
 }
 return cookieValue;
}

function getCSRFToken(){
 const cookie = getCookie("csrftoken");
 if(cookie) return cookie;
 const input = document.querySelector("input[name='csrfmiddlewaretoken']");
 return input ? input.value : "";
}

async function api(path, options={}){
 const method=(options.method||"GET").toUpperCase();
 const headers={"Content-Type":"application/json",...(options.headers||{})};

 if(["POST","PUT","PATCH","DELETE"].includes(method)){
   const csrf=getCSRFToken();
   if(csrf) headers["X-CSRFToken"]=csrf;
 }

 const response=await fetch("/api"+path,{
   credentials:"same-origin",
   ...options,
   headers
 });

 const data=await response.json().catch(()=>({}));

 if(!response.ok){
   let message="Request failed.";
   if(data.detail) message=data.detail;
   else if(data.non_field_errors) message=data.non_field_errors.join(" ");
   else {
     const parts=[];
     Object.entries(data).forEach(([field,error])=>{
       if(Array.isArray(error)) parts.push(`${field}: ${error.join(" ")}`);
       else if(typeof error==="object") parts.push(`${field}: ${JSON.stringify(error)}`);
       else parts.push(`${field}: ${error}`);
     });
     if(parts.length) message=parts.join(" | ");
   }
   throw new Error(message);
 }
 return data;
}

function formToJSON(form){
 const fd=new FormData(form), obj={};
 fd.forEach((v,k)=>{
   if(k!=="csrfmiddlewaretoken") obj[k]=v;
 });
 return obj;
}

function escapeHtml(v){
 return String(v??"").replace(/[&<>"']/g,c=>({
   "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"
 }[c]));
}

function clearErrors(form){
 form.querySelectorAll(".field-error").forEach(x=>x.textContent="");
 form.querySelectorAll(".api-error").forEach(x=>x.remove());
}

function showApiError(form,error){
 let box=form.querySelector(".api-error");
 if(!box){
   box=document.createElement("div");
   box.className="alert alert-danger api-error col-12";
   form.prepend(box);
 }
 box.textContent=error.message;
}
function apiList(data){
  if(Array.isArray(data)) return data;
  if(data && Array.isArray(data.results)) return data.results;
  return [];
}
