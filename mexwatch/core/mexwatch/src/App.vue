<template>
	<div id="app">
		<alert type="success/info/danger/warning">
	</alert>

	<alert :show.sync="showRight" placement="top-right" duration="3000" type="success" width="400px" dismissable>
		<span class="icon-ok-circled alert-icon-float-left"></span>
		<strong>Well Done!</strong>
		<p>You successfully read this important alert message.</p>
	</alert>

	<alert :show.sync="showTop" placement="top" duration="3000" type="danger" width="400px" dismissable>
		<span class="icon-info-circled alert-icon-float-left"></span>
		<strong>Heads up!</strong>
		<p>This alert needs your attention.</p>
	</alert>
		<router-view/>
	</div>
</template>

<script>
export default {
	name: 'App'
}
</script>

<style>
#app {
	font-family: 'Avenir', Helvetica, Arial, sans-serif;
	-webkit-font-smoothing: antialiased;
	-moz-osx-font-smoothing: grayscale;
	text-align: center;
	color: #2c3e50;
	margin-top: 60px;
}
</style>
