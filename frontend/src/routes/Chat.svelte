<script>
	import fastapi from "../lib/api"
    import ChatBox from "./ChatBox.svelte";
	import { is_login } from "../lib/store"
    import { fas } from "@fortawesome/free-solid-svg-icons";

    let data = [];
	let query = '';
	let error = {detail:[]}

    let current = [];
    let data_index = 0;
    let current_index = 0;

    function readingTime(text) {
        const wps = 225 / 60;
        const words = text.trim().split(/\s+/).length;
        const time = Math.ceil((words / wps) * 2000);
        return time;
    }

    let accumulated_time = 0;
	function accumulate(text, is_user) {
		const time = readingTime(text);
        const _data = {
            text: text,
			who: is_user,
	        ready: false,
            isolateDelay: time,
    	    delay: accumulated_time + (time < 1500 ? 1500 : time * 2),
		};
    	accumulated_time = _data.delay;
		data.push(_data)
	}

	function run() {
		if (data[current_index].text === "") return;
    	const delay = data[data_index].isolateDelay;  // 메시지마다 다른 지연 시간
		current.push(data[data_index++]);
		current = current
    	setTimeout(() => {
			current[current_index++].ready = true                                                                     
    	}, delay);
	}

    function trigger() {
        requestAnimationFrame(run);
    }

	function start_gemini() {
		let url = "/api/chat/start"
		accumulate("", "gemini")
		fastapi('get', url, {}, 
			(json) => {
				data[data_index].text = json
				trigger()
			})
	}

    function query_gemini() {
		let url = "/api/chat/query"
        let params = {
            content: query
        }
		accumulate(query, "you")
		accumulate("", "gemini")
		trigger()
		fastapi('post', url, params, 
            (json) => {
				data[data_index].text = json
				query = ''
				trigger()
            },
            (err_json) => {
                error = err_json
            }
        )
    }

	start_gemini()
</script>

<div class="card card-danger direct-chat direct-chat-danger">
	<div>
    {#each current as { text, who, ready, isolateDelay }}
        <ChatBox {who} {text} {ready} {isolateDelay} />
    {/each}
	</div>
</div>
<div class="card">
	<div class="input-group">
		<input type="text" placeholder="Type Message ..." class="form-control"
		 disabled={$is_login ? "" : "disabled"} bind:value={query}>
		<span class="input-group-append">
			<button type="button" class="btn btn-primary" disabled={$is_login ? "" : "disabled"}
			on:click="{query_gemini}">Send</button>
		</span>
	</div>
</div>

<style>
	.card {
		width: 750px;
		margin: 50px auto;
		padding: 20px;
		overflow-x: hidden;
		position: relative;
	}
</style>
