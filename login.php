<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="UTF-8">
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<title>Login</title>
	
	<link rel="stylesheet" href="css/bootstrap.min.css">
</head>
<body>
	<div class="container">
		<div class="row justify-content-center mt-5">
			<div class="col-md-6">
				<?php
					// Tampilkan pesan error jika ada
					session_start();
					if (isset($_SESSION['error'])) {
						echo '<div class="alert alert-danger" role="alert">';
						echo $_SESSION['error'];
						echo '</div>';
						unset($_SESSION['error']);
					}
				?>
				<div class="card">
					<div class="card-header">
						<h5 class="card-title">Login</h5>
					</div>
					<div class="card-body">
						<form method="POST" action="process-login.php">
							<div class="mb-3">
								<label for="username" class="form-label">Username</label>
								<input type="text" name="username" class="form-control" id="username" required>
							</div>
							<div class="mb-3">
								<label for="password" class="form-label">Password</label>
								<input type="password" name="password" class="form-control" id="password" required>
							</div>
							<button type="submit" class="btn btn-primary">Login</button>
						</form>
					</div>
				</div>
			</div>
		</div>
	</div>
	<!-- Bootstrap JS -->
	<script src="js/bootstrap.min.js"></script>
	
