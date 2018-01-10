<?php 

	function api_call($url, $method = 'GET', $data = []) {
		$apiKey = '4YFgfRe713-feq7ovWHtl_da';
		$apiSecret = 'SWkuxaufF9G2n_YgLONCAKAvtPBwBBYy17ZW0Fn8kH2iUs0m'; 
		$apiUrl = 'https://www.bitmex.com';

		// $priv = $_GET['priv'];
		// $pub = $_GET["pub"];
		// $testnet = $_GET["testnet"];

		// if((!empty($testnet))) {
		// 	$apiUrl = 'https://testnet.bitmex.com';
		// }

		// if((!empty($priv)) && (!empty($priv))) {
		// 	$apiKey = $pub;
		// 	$apiSecret = $priv;
		// }

		$verb = 'GET';
		$path = '/api/v1'.$url;
		$expires = (time()+60) ; // 1 min in the future

		$data_url = "?".http_build_query($data, '', '&amp;');
		// echo "<pre>";
		// print_r($data_url);
		// echo "</pre>";
		$signature = hash_hmac('sha256', $verb.$path.$data_url.$expires, $apiSecret);

		$c = curl_init();
		curl_setopt_array($c, [
			CURLOPT_URL => $apiUrl.$path.$data_url,  //dfgdsfgsdgsdfgsdfgsdfg
			CURLOPT_SSL_VERIFYPEER => 0,
			CURLOPT_SSL_VERIFYHOST => 0,
			CURLOPT_RETURNTRANSFER => true,
			CURLOPT_FOLLOWLOCATION => true,
			CURLOPT_HTTPHEADER => [
				'api-expires: '.$expires,
				'api-key: '.$apiKey,
				'api-signature: '.$signature
			],
		]);

		$response = curl_exec($c);

		return $response;
	}


	function textToColor($str) {
	  $code = dechex(crc32($str));
	  $code = substr($code, 0, 6);
	  return $code;
	}

?>
<!DOCTYPE html>
<html lang="en-US">
	<head>
		<meta charset="utf-8">
		<meta http-equiv="X-UA-Compatible" content="IE=edge">
		<meta name="robots" content="noindex, nofollow">
		<meta name="viewport" content="width=device-width, initial-scale=1">
		<title>Bitmex Watcher</title>
		<link rel="icon" type="image/png" href="icon.png?v=2" />
		<!-- Bootstrap CSS -->
		<link href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" rel="stylesheet">
		<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css">
		<link rel="stylesheet" href="darkly.css">
		<link rel="stylesheet" href="style.css">
		<!-- jQuery -->
		<script src="https://ajax.googleapis.com/ajax/libs/jquery/1.12.0/jquery.min.js"></script>
		<!-- Bootstrap JavaScript -->
		<script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>
		<!-- HTML5 Shim and Respond.js IE8 support of HTML5 elements and media queries -->
		<!-- WARNING: Respond.js doesn't work if you view the page via file:// -->
		<!--[if lt IE 9]>
			<script src="https://oss.maxcdn.com/html5shiv/3.7.2/html5shiv.min.js"></script>
			<script src="https://oss.maxcdn.com/respond/1.4.2/respond.min.js"></script>
		<![endif]-->
		<style>
		.contain-pre { max-width: 100%; overflow-y: scroll; display: block; }
			a { transition: all 300ms; }
			a:focus,
			a:hover,
			a:active { text-decoration: none; }
			a:hover { color: #7CFFDE !important; }
			body { font-size: 16px; }
			.main { padding-top: 3em; position: relative; }
			.tab-pane { padding-top: 15px; }
			#tabs_main + .panel-group .panel-heading { padding: 0; }
			#tabs_main + .panel-group .panel-heading a { padding: 10px 15px; display: block; }
			
			tr[data-order-type="Sell"] td:first-child	{ border-left: 4px solid #ff0000 !important; }
			tr[data-order-type="Buy"] td:first-child	{ border-left: 4px solid #00ff00 !important; }


			tr[data-order-type="Sell"] td:nth-child(2)		{ color: #ff0000; }
			tr[data-order-type="Buy"] td:nth-child(2)		{ color: #00ff00; }
			td { white-space: nowrap; }
			body { overflow-y: scroll; }
			
			.refresh_btn { border: 1px solid transparent !important; background: none !important; opacity: 0.8; transition: opacity 300ms, transform 500ms ease-in-out; cursor: pointer;
				display: inline-block; padding: 10px 15px; }
			.refresh_btn:hover { opacity: 1; transform: rotate(360deg); }
			.tab_inner { opacity: 0; transition: opacity 600ms ease-out; }
			.loaded .tab_inner { opacity: 1; }

			.corner_balance { position: absolute; right: 5px; top: 5px; display: inline-block; font-size: 16px; font-weight: bold;
				color: #f39c12; }
		</style>
	</head>
	<body>
		<div class="main">
			<div class="corner_balance">
				<?php $wallet_data = json_decode(api_call('/user/wallet'), true); ?>
				<span title="Total balance"><?php echo round($wallet_data["amount"]/100000000,3); ?> BTC</span>
			</div>
			<!-- <pre> -->
				<?php //print_r($wallet_data); ?>
			<!-- </pre> -->
			<div class="container">
				<ul id="tabs_main" class="nav nav-tabs">
					<li class="active"><a href="#positions_tab" data-toggle="tab">Positions</a></li>
					<li><a href="#closed_positions_tab" data-toggle="tab">Closed Positions</a></li>
					<li><a href="#active_orders_tab" data-toggle="tab">Active Orders</a></li>
					<li><a href="#stops" data-toggle="tab">Stops</a></li>
					<li><a href="#fills" data-toggle="tab">Fills</a></li>
					<li><a href="#order_history" data-toggle="tab">Order History</a></li>
					<li><span class="refresh_btn"><i class="fa fa-refresh text-success"></i></span></li>
				</ul>
				<div id="myTabContent" class="tab-content">
					<div class="tab-pane fade in active" id="positions_tab">
						<div class="positions_tab_inner tab_inner">
							<?php 
								$positions = json_decode(api_call('/position'), true);

							
							 ?>
							<table class="table table-striped">
								<thead>
									<tr>
										<th>Symbol</th>
										<th>Size</th>
										<th>Value</th>
										<th>Entry Price</th>
										<th>Mark Price</th>
										<th>Liq. Price</th>
										<th>Margin</th>
										<th>Unrealised PNL<!--  (ROE %) --></th>
										<th>Realised PNL</th>
									</tr>
									<tbody>
										
									<?php 
										$satoshis_per_btc = 100000000;
										foreach ($positions as $position) { ?>
											<tr>
												<td><?php echo $position["symbol"]; ?></td>
												<td><?php echo $position["currentQty"]; ?></td>
												<td><?php echo $position["currentQty"] * $position["markPrice"] . "XBT"; ?></td>
												<td><?php echo $position["avgEntryPrice"]; ?></td>
												<td><?php echo $position["markPrice"]; ?></td>
												<td><?php echo $position["liquidationPrice"]; ?></td>
												<td><?php echo round($position["maintMargin"]/$satoshis_per_btc, 2) . ($position["crossMargin"] == "1" ? " (Cross)" : ""); ?></td>
												<td>
													<?php echo round($position["simplePnl"],4); ?> XBT
													<?php //echo $position["unrealisedRoePcnt"]*100 . "%"; ?>
												</td>
												<td><?php echo round(($position["rebalancedPnl"]+$position["realisedPnl"])/$satoshis_per_btc, 4); ?> XBT</td>
											</tr>
										<?php }
									?>
									</tbody>
								</thead>
							</table>

							<?php 

							echo "<pre>";
							print_r(json_decode(api_call('/position'), true));
							echo "</pre>";

							 ?>
						</div>
					</div>
					<div class="tab-pane fade" id="closed_positions_tab">
						<div class="closed_positions_tab_inner tab_inner">
							<?php //api_call('/position'); ?>
						</div>
					</div>
					<div class="tab-pane fade" id="active_orders_tab">
						<div class="active_orders_tab_inner tab_inner">
							<?php //api_call('/position'); ?>
						</div>
					</div>
					<div class="tab-pane fade" id="stops">
						<div class="stops_tab_inner tab_inner">
							<?php //api_call('/position'); ?>
						</div>
					</div>
					<div class="tab-pane fade" id="fills">
						<div class="fills_inner tab_inner">
							<?php $fills = json_decode(api_call('/execution/tradeHistory',"GET", [
								'reverse' => true
								]), true); ?>

							<table class="table table-striped">
								<thead>
									<tr>
										<th>Symbol</th>
										<th>Qty</th>
										<th>Exec Qty</th>
										<th>Remaining</th>
										<th>Exec Price</th>
										<th>Price</th>
										<th>Value</th>
										<th>Type</th>
										<th>OrderID</th>
										<th>Time</th>
									</tr>
									<tbody>
										
									<?php 
										foreach ($fills as $fill) { 
											if(!empty($fill["side"])) { ?>
											<tr data-order-type="<?php echo $fill["side"]; ?>">
												<td><?php echo $fill["symbol"]; ?></td>
												<td><?php echo $fill["orderQty"]; ?></td>
												<td><?php echo $fill["lastQty"]; ?></td>
												<td><?php echo $fill["simpleLeavesQty"]; ?></td>
												<td><?php echo $fill["price"]; ?></td>
												<td>
													<?php 
														if ($fill["ordType"] == "Market") {
															echo "Market";
														} else {
															echo $fill["price"];
														}

													?>
														
												</td>
												<td><?php echo $fill["foreignNotional"]; ?> XBT</td>
												<td><?php echo $fill["ordType"]; ?></td>
												<td <?php $ord_ID = substr($fill["orderID"],0,7); ?> style="color: #<?php echo textToColor($ord_ID); ?>"><?php echo $ord_ID; ?></td>
												<td><?php echo date("M d, Y, H:i:s",strtotime($fill['timestamp'])); ?></td>
											</tr>
											<?php }
											}
									?>
									</tbody>
								</thead>
							</table>


							<?php 
								echo "<pre>";
								print_r($fills);
								echo "</pre>";
							 ?>
						</div>
					</div>
					<div class="tab-pane fade" id="order_history">
						<div class="order_history_inner">
							<?php //api_call('/position'); ?>
						</div>
					</div>
				</div>
				<!-- <br> -->
			</div>
		</div>
		<script>
			$(function() {
				$("body").addClass("loaded");
				// curl -X GET --header 'Accept: application/json' 'https://testnet.bitmex.com/api/v1/position'
				$('.refresh_btn').click(function(ev) {
					ev.preventDefault();
					$("body").removeClass("loaded");
					setTimeout(function() { 
						location.reload(); 
					}, 500);
				});
			});


			$('#tabs_main a').click(function(e) {
			  e.preventDefault();
			  $(this).tab('show');
			});

			// store the currently selected tab in the hash value
			$("ul.nav-tabs > li > a").on("shown.bs.tab", function(e) {
				var id = $(e.target).attr("href").substr(1);
				window.location.hash = id;
				window.scrollTo(0, 0);
			});

			// on load of the page: switch to the currently selected tab
			var hash = window.location.hash;
			$('#tabs_main a[href="' + hash + '"]').tab('show');
			
		</script>
	</body>
</html>