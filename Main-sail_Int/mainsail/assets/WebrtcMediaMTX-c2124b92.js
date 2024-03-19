import{m as p,B as m,G as f,P as h,W as u,R as g,C as _,n as T}from"./index-c1d4ed42.js";import{l as w,m as v,p as C}from"./vuetify-53c5c501.js";import"./overlayscrollbars-44d87bcf.js";import"./echarts-9bc570b0.js";var S=Object.defineProperty,y=Object.getOwnPropertyDescriptor,d=(n,e,t,i)=>{for(var s=i>1?void 0:i?y(e,t):e,r=n.length-1,a;r>=0;r--)(a=n[r])&&(s=(i?a(e,t,s):a(s))||s);return i&&s&&S(e,t,s),s};let o=class extends p(m,f){constructor(){super(...arguments),this.pc=null,this.restartTimeout=null,this.status="connecting",this.eTag=null,this.queuedCandidates=[],this.offerData={iceUfrag:"",icePwd:"",medias:[]},this.RESTART_PAUSE=2e3,this.unquoteCredential=e=>JSON.parse('"'.concat(e,'"'))}beforeDestroy(){this.terminate(),this.restartTimeout&&clearTimeout(this.restartTimeout)}get webcamStyle(){var e,t,i;return{transform:this.generateTransform((e=this.camSettings.flip_horizontal)!=null?e:!1,(t=this.camSettings.flip_vertical)!=null?t:!1,(i=this.camSettings.rotation)!=null?i:0)}}get url(){let e=this.camSettings.stream_url;return e.endsWith("/")||(e+="/"),e=new URL("whep",e).toString(),this.convertUrl(e,this.printerUrl)}changedUrl(){this.terminate(),this.start()}get expanded(){var e;return(e=this.$store.getters["gui/getPanelExpand"]("webcam-panel",this.viewport))!=null?e:!1}expandChanged(e){if(!e){this.terminate();return}this.start()}log(e,t){if(t){window.console.log("[WebRTC mediamtx] ".concat(e),t);return}window.console.log("[WebRTC mediamtx] ".concat(e))}linkToIceServers(e){return e===null?[]:e.split(", ").map(t=>{const i=t.match(/^<(.+?)>; rel="ice-server"(; username="(.*?)"; credential="(.*?)"; credential-type="password")?/i);if(i===null)return{urls:""};const s={urls:[i[1]]};return i.length>3&&(s.username=this.unquoteCredential(i[3]),s.credential=this.unquoteCredential(i[4]),s.credentialType="password"),s})}parseOffer(e){const t={iceUfrag:"",icePwd:"",medias:[]};for(const i of e.split("\r\n"))i.startsWith("m=")?t.medias.push(i.slice(2)):t.iceUfrag===""&&i.startsWith("a=ice-ufrag:")?t.iceUfrag=i.slice(12):t.icePwd===""&&i.startsWith("a=ice-pwd:")&&(t.icePwd=i.slice(10));return t}generateSdpFragment(e,t){const i={};for(const a of t){const c=a.sdpMLineIndex;c!==null&&(c in i||(i[c]=[]),i[c].push(a))}let s="a=ice-ufrag:"+e.iceUfrag+"\r\na=ice-pwd:"+e.icePwd+"\r\n",r=0;for(const a of e.medias){if(i[r]!==void 0){s+="m="+a+"\r\na=mid:"+r+"\r\n";for(const c of i[r])s+="a="+c.candidate+"\r\n"}r++}return s}start(){this.log("requesting ICE servers from "+this.url),fetch(this.url,{method:"OPTIONS"}).then(e=>this.onIceServers(e)).catch(e=>{this.log("error: "+e),this.scheduleRestart()})}onIceServers(e){const t=this.linkToIceServers(e.headers.get("Link"));this.log("ice servers:",t),this.pc=new RTCPeerConnection({iceServers:t});const i="sendrecv";this.pc.addTransceiver("video",{direction:i}),this.pc.addTransceiver("audio",{direction:i}),this.pc.onicecandidate=s=>this.onLocalCandidate(s),this.pc.oniceconnectionstatechange=()=>this.onConnectionState(),this.pc.ontrack=s=>{this.log("new track:",s.track.kind),this.video.srcObject=s.streams[0]},this.pc.createOffer().then(s=>this.onLocalOffer(s))}onLocalOffer(e){var t,i;this.offerData=this.parseOffer((t=e.sdp)!=null?t:""),(i=this.pc)==null||i.setLocalDescription(e),fetch(this.url,{method:"POST",headers:{"Content-Type":"application/sdp"},body:e.sdp}).then(s=>{if(s.status!==201)throw new Error("bad status code");return this.eTag=s.headers.get("ETag"),s.headers.has("E-Tag")&&(this.eTag=s.headers.get("E-Tag")),s.text()}).then(s=>{this.onRemoteAnswer(new RTCSessionDescription({type:"answer",sdp:s}))}).catch(s=>{this.log(s),this.scheduleRestart()})}onRemoteAnswer(e){var t;this.restartTimeout===null&&((t=this.pc)==null||t.setRemoteDescription(e),this.queuedCandidates.length!==0&&(this.sendLocalCandidates(this.queuedCandidates),this.queuedCandidates=[]))}onConnectionState(){var e,t;if(this.restartTimeout===null)switch(this.status=(t=(e=this.pc)==null?void 0:e.iceConnectionState)!=null?t:"",this.log("peer connection state:",this.status),this.status){case"disconnected":this.scheduleRestart()}}onLocalCandidate(e){if(this.restartTimeout===null&&e.candidate!==null){if(this.eTag===""){this.queuedCandidates.push(e.candidate);return}this.sendLocalCandidates([e.candidate])}}sendLocalCandidates(e){fetch(this.url,{method:"PATCH",headers:{"Content-Type":"application/trickle-ice-sdpfrag","If-Match":this.eTag},body:this.generateSdpFragment(this.offerData,e)}).then(t=>{if(t.status!==204)throw new Error("bad status code")}).catch(t=>{this.log(t),this.scheduleRestart()})}terminate(){this.log("terminating"),this.pc!==null&&(this.pc.close(),this.pc=null)}scheduleRestart(){this.restartTimeout===null&&(this.terminate(),this.restartTimeout=window.setTimeout(()=>{this.log("scheduling restart"),this.restartTimeout=null,this.start()},this.RESTART_PAUSE),this.eTag="",this.queuedCandidates=[])}};d([h({required:!0})],o.prototype,"camSettings",2);d([h({default:null})],o.prototype,"printerUrl",2);d([g()],o.prototype,"video",2);d([u("url")],o.prototype,"changedUrl",1);d([u("expanded",{immediate:!0})],o.prototype,"expandChanged",1);o=d([_],o);var b=function(){var n=this,e=n.$createElement,t=n._self._c||e;return t("div",[t("video",{directives:[{name:"show",rawName:"v-show",value:n.status==="connected",expression:"status === 'connected'"}],ref:"video",staticClass:"webcamImage",style:n.webcamStyle,attrs:{autoplay:"",playsinline:"",muted:""},domProps:{muted:!0}}),n.status!=="connected"?t(w,[t(v,{staticClass:"_webcam_webrtc_output text-center d-flex flex-column justify-center align-center"},[n.status==="connecting"?t(C,{staticClass:"mb-3",attrs:{indeterminate:"",color:"primary"}}):n._e(),t("span",{staticClass:"mt-3"},[n._v(n._s(n.status))])],1)],1):n._e()],1)},x=[];const l={};var R=T(o,b,x,!1,P,"781d4888",null,null);function P(n){for(let e in l)this[e]=l[e]}const q=function(){return R.exports}();export{q as default};
