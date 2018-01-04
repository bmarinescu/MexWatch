<?php 

	function api_call($url, $method = 'GET', $data = []) {
		$apiKey = 'kuKCNxKcyd0jKRPG3fRxAUFk';
		$apiSecret = 'aUY4oUm5zhCTbQAsayM7iwwsiuKvgIpuXU-MaRI15hL5Daih'; 

		$verb = 'GET';
		$path = '/api/v1'.$url;
		$expires = (time()+60) ; // 1 min in the future

		$signature = hash_hmac('sha256', $verb.$path.$expires, $apiSecret);

		$c = curl_init();
		curl_setopt_array($c, [
			CURLOPT_URL => 'https://testnet.bitmex.com'.$path,
			CURLOPT_SSL_VERIFYPEER => 0,
			CURLOPT_SSL_VERIFYHOST => 0,
			CURLOPT_RETURNTRANSFER => true,
			CURLOPT_FOLLOWLOCATION => true,
			CURLOPT_HTTPHEADER => [
				'api-expires: '.$expires,
				'api-key: '.$apiKey,
				'api-signature: '.$signature
			]
		]);

		$response = curl_exec($c);

		return $response;
	}


	
?>
<!DOCTYPE html>
<html lang="">
	<head>
		<meta charset="utf-8">
		<meta http-equiv="X-UA-Compatible" content="IE=edge">
		<meta name="robots" content="noindex, nofollow">
		<meta name="viewport" content="width=device-width, initial-scale=1">
		<title>mx</title>
		<!-- Bootstrap CSS -->
		<link href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" rel="stylesheet">
		<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css">
		<link rel="stylesheet" href="darkly.css">
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
			.main { padding-top: 3em; }
			.tab-pane { padding-top: 15px; }
			#tabs_main + .panel-group .panel-heading { padding: 0; }
			#tabs_main + .panel-group .panel-heading a { padding: 10px 15px; display: block; }

			
		</style>
	</head>
	<body>
		<div class="main">
			<div class="container">
				<ul id="tabs_main" class="nav nav-tabs">
					<li class="active"><a href="#positions_tab" data-toggle="tab">Positions</a></li>
					<li><a href="#closed_positions_tab" data-toggle="tab">Closed Positions</a></li>
					<li><a href="#active_orders_tab" data-toggle="tab">Active Orders</a></li>
					<li><a href="#stops" data-toggle="tab">Stops</a></li>
					<li><a href="#fills" data-toggle="tab">Fills</a></li>
					<li><a href="#order_history" data-toggle="tab">Order History</a></li>
				</ul>
				<div id="myTabContent" class="tab-content">
				    <div class="tab-pane fade in active" id="positions_tab">
				       	<div class="positions_tab_inner">
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
				       					foreach ($positions as $position) { ?>
											<tr>
												<td><?php echo $position["symbol"]; ?></td>
												<td><?php echo $position["currentQty"]; ?></td>
												<td><?php echo (-1)*$position["homeNotional"]; ?> <?php echo $position["underlying"]; ?></td>
												<td><?php echo $position["avgEntryPrice"]; ?></td>
												<td><?php echo $position["lastPrice"]; ?></td>
												<td><?php echo $position["liquidationPrice"]; ?></td>
												<td><?php echo $position["crossMargin"]; ?></td>
												<td>
													<?php echo $position["simplePnl"]; ?>
													<?php //echo $position["unrealisedRoePcnt"]*100 . "%"; ?>
												</td>
												<td><?php echo $position["realisedGrossPnl"]; ?></td>
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
				        <div class="closed_positions_tab_inner">
				        	<?php //api_call('/position'); ?>
				        </div>
				    </div>
				    <div class="tab-pane fade" id="active_orders_tab">
				        <div class="active_orders_tab_inner">
				        	<?php //api_call('/position'); ?>
				        </div>
				    </div>
				    <div class="tab-pane fade" id="stops">
				        <div class="stops_inner">
				        	<?php //api_call('/position'); ?>
				        </div>
				    </div>
				    <div class="tab-pane fade" id="fills">
				        <div class="fills_inner">
				        	<?php //api_call('/position'); ?>
				        </div>
				    </div>
				    <div class="tab-pane fade" id="order_history">
				        <div class="order_history_inner">
				        	<?php //api_call('/position'); ?>
				        </div>
				    </div>
				</div>
				<br>

				<?php 
					// echo "<div class='contain-pre'>";
					// print_r(api_call('/position'));
					// echo "</div>";
					
					// echo "<pre>";
					// $execution = json_decode(api_call('/execution'), true);
					// print_r($execution);
					// echo "</pre>";
				?>
			</div>
		</div>
		<script>
			$(function() {
				
				// curl -X GET --header 'Accept: application/json' 'https://testnet.bitmex.com/api/v1/position'

			});
				
		</script>
	</body>
</html>