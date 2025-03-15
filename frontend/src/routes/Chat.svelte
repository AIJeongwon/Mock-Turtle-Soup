<script>
	import fastapi from "../lib/api"
    import ChatBox from "./ChatBox.svelte"
	import { is_login, api_key } from "../lib/store"

    let data = []
	let current = []
	let query = ''
	let _api_key = ''
	let regex = /^[a-z | A-Z | ~!@#$%^&*()_+|<>?:{}]/
	let error = {detail:[]}

    let data_index = 0
    let current_index = 0
	let is_saved = ($api_key !== "" )

	function save_key() {
		if (is_saved) {
			is_saved = false
			$api_key = ''
		}
		else {
			if (regex.test(_api_key)) {
				is_saved = true
				$api_key = _api_key
				start_gemini()
			}
			else
				console.log("API Key validation error!")
		}
	}

    function readingTime(text) {
        const wps = 225 / 60;
        const words = text.trim().split(/\s+/).length
        const time = Math.ceil((words / wps) * 2000)
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
		}
    	accumulated_time = _data.delay
		data.push(_data)
	}

	function run() {
		if (data[current_index].text === "") return
    	const delay = data[data_index].isolateDelay  // 메시지마다 다른 지연 시간
		current.push(data[data_index++])
		current = current
    	setTimeout(() => {
			current[current_index++].ready = true                                                                     
    	}, delay)
	}

    function trigger() {
        requestAnimationFrame(run)
    }

	function start_gemini() {
		let url = "/api/chat/start"
		let params = {
			key: $api_key
		}
		accumulate("", "gemini")
		fastapi('post', url, params, 
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

	// API key가 저장되어 있는 경우, 바로 챗 시작
	if (is_saved)
		start_gemini()

</script>

<div class="top-container">
	<div class="input-group">
		<input type="form-control" placeholder="Type Your API Key ..." class="form-control"
		 disabled={$is_login && !is_saved ? "" : "disabled"} bind:value={_api_key}>
		<span class="input-group-append">
			<button type="button" class="btn btn-primary" disabled={$is_login ? "" : "disabled"}
			on:click="{save_key}">
			{#if is_saved}
				API Key 수정
			{:else}
				API Key 저장
			{/if}
			</button>
		</span>
	</div>
</div>
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
		 disabled={$is_login && is_saved? "" : "disabled"} bind:value={query}>
		<span class="input-group-append">
			<button type="button" class="btn btn-primary" disabled={$is_login && is_saved ? "" : "disabled"}
			on:click="{query_gemini}">Send</button>
		</span>
	</div>
</div>

<style>
	.card {
		width: 750px;
		margin: 30px auto;
		padding: 20px;
		overflow-x: hidden;
		position: relative;
	}
	.top-container {
		position: relative;
    	text-align: left;
		width: 400px;
		padding: 20px;
	}
</style>
