<script>
    import { onMount, tick } from "svelte";
	import fastapi from "../lib/api"
    import ChatBox from "./ChatBox.svelte";

    let data = [];
	let query = '';
	let error = {detail:[]}

    let current = [];
    let timer = 0;
    let current_index = 0;

    function readingTime(text) {
        const wps = 225 / 60;
        const words = text.trim().split(/\s+/).length;
        const time = Math.ceil((words / wps) * 1000);
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
		data[current_index].ready= true;
		current.push(data[current_index++]); 
		current = current;
		requestAnimationFrame(run)   
	}

    function trigger() {
        requestAnimationFrame(run);
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
				data[current_index].text = json
				query = ''
				trigger()
				console.log(current)
            },
            (err_json) => {
                error = err_json
            }
        )
    }
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
		<input type="text" placeholder="Type Message ..." class="form-control" bind:value={query}>
		<span class="input-group-append">
			<button type="button" class="btn btn-primary" on:click="{query_gemini}">Send</button>
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
