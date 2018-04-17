	<!-- stylesheet should normally go inside <head>, otherwise use property attribute -->
	<link rel="stylesheet" property="stylesheet" href="css/jquery-ui.css">
			<form action="modify.php" method="post" enctype="multipart/form-data">
					<label for="uploadfile">Upload file: </label><input type="file" class="arg" name="filename" accept=".txt,.out" id="uploadfile" required><br>
					<label for="datepicker">Processing date: </label><input type="text" class="arg" name="date" id="datepicker" required><br>
					<label for="organization">Organization: </label>
					<select class="arg" name="organization" id="organization" required>
						<option value="">Select Organization</option>
						<option value="CLB">CLB</option>
						<option value="LSO">LSO</option>
					</select><br>
					<input type="submit" class="button" value="Submit">
			</form>
			<script src="js/jquery-1.10.2.js"></script>
			<script src="js/jquery-ui.js"></script>
			<script>
				$(function() {
					$( "#datepicker" ).datepicker();
				});
			</script>
