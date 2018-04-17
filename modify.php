<?php 

include "template.class.php";
require_once "functions.php";

$target_dir = "uploads/";
$target_file = $target_dir . basename($_FILES["filename"]["name"]);
$ext = pathinfo($target_file, PATHINFO_EXTENSION);

$pDate = $_POST['date'];
$ORGid = $_POST['organization'];
$outFile = "uploads/MO_COLUM_" . $ORGid . "_UMAP0007.TXT";
$tmpFile = "uploads/MO_COLUM_" . $ORGid . "_UMAP0007.TMP";

list ($uploadOk, $errStr) = checkArgs($ext, $pDate, $ORGid);
if ($uploadOk) 
{
	if (move_uploaded_file($_FILES["filename"]["tmp_name"], $target_file))
	{
		$filename = basename($target_file);
		$command = './s2ps.py '.escapeshellarg($target_file)." $pDate $ORGid uploads/";
		$output = exec($command.' 2>&1', $retArr, $retVal);
		if($retVal == 1)
		{
			foreach ($retArr as $line)
			{
				$errLine = new Template("errline.tpl");
				$errLine->set("line", $line);
				$errLines[] = $errLine;
			}
			$errContents = Template::merge($errLines, "");

			$header = new Template("header.tpl");
			$header->set("title", "Sierra to PeopleSoft");
			$header->set("heading", "Sierra to PeopleSoft");
			$header->set("subheading", "Error");

			$content = new Template("error.tpl");
			$content->set("heading", "Parsing Error");
			$content->set("command", $command); 
			$content->set("stdout", $errContents);

			$footer = new Template("footer.tpl");
			$footer->set("email", "");

			$layout = new Template("layout.tpl");
			$layout->set("header", $header->output());
			$layout->set("content", $content->output());
			$layout->set("footer", $footer->output());

			echo $layout->output();
		}	
		else
		{
			if($ORGid == "LSO") 
			{
				if( rename($outFile, $tmpFile) )
				{	
					$transactionArray = getTransactions($tmpFile);
					foreach ($transactionArray as $transactionRows)
					{
						$trTemplates = array();
						foreach($transactionRows as $transactionStr)
						{
							$transactionStr = preg_replace('!\s+!', ' ', $transactionStr);
							$transactionStr = rtrim($transactionStr);
							$trTpl = new Template("modify_trans.tpl");
							$trTpl->set("row", $transactionStr);
							$trTemplates[] = $trTpl;
						}
						$trContents[] = Template::merge($trTemplates, "\t\t");
					}
					$rows = file($tmpFile);
					$count = 0;
					foreach ($rows as $row) 
					{
						if(contains("INSERTDESC", $row)) 
						{
							$rowTpl = new Template("modify_rows.tpl");
							$rowTpl->set("trans", $trContents[$count]);
							$rowTpl->set("count", $count);
							$count++;
							$rowTemplates[] = $rowTpl;
						}

					}
					$rowTpl = new Template("hidden_org.tpl");
					$rowTpl->set("ORGid", $ORGid);
					$rowTemplates[] = $rowTpl;
					$rowContents = Template::merge($rowTemplates);
					
					$header = new Template("header.tpl");
					$header->set("title", "Sierra to PeopleSoft");
					$header->set("heading", "Sierra to PeopleSoft");
					$header->set("subheading", "(LSO) File modification");

					$content = new Template("modify.tpl");
					$content->set("inputfile", $filename);
					$content->set("organization", $ORGid);
					$content->set("date", $pDate);
					$content->set("outputfile", basename($tmpFile));
					$content->set("modify_rows", $rowContents);

					$footer = new Template("footer.tpl");
					$footer->set("email", "");

					$layout = new Template("layout.tpl");
					$layout->set("header", $header->output());
					$layout->set("content", $content->output());
					$layout->set("footer", $footer->output());

					echo $layout->output();
				}
				else
				{
					$header = new Template("header.tpl");
					$header->set("title", "Sierra to PeopleSoft");
					$header->set("heading", "Sierra to PeopleSoft");
					$header->set("subheading", "Error");

					$content = new Template("error.tpl");
					$content->set("heading", "Server Error");
					$content->set("command", "N/A"); 
					// This shouldn't ever really happen. Usual cause is misconfigured permissions, which would result in a failed move error prior to the rename.
					$content->set("stdout", "Failed to rename file. Check permissions on upload directory.");

					$footer = new Template("footer.tpl");
					$footer->set("email", "");

					$layout = new Template("layout.tpl");
					$layout->set("header", $header->output());
					$layout->set("content", $content->output());
					$layout->set("footer", $footer->output());

					echo $layout->output();
				}
			}
			else if($ORGid == "CLB") 
			{
				$rowTpl = new Template("hidden_org.tpl");
				$rowTpl->set("ORGid", $ORGid);
				$rowTemplates[] = $rowTpl;
				$rowContents = Template::merge($rowTemplates);
				
				$header = new Template("header.tpl");
				$header->set("title", "Sierra to PeopleSoft");
				$header->set("heading", "Sierra to PeopleSoft");
				$header->set("subheading", "(CLB) Download");

				$content = new Template("download.tpl");
				$outLink = "<a href=\"$outFile";
				$outLink .= "\" id=\"download\" download>Download file</a>";
				$content->set("downloadLink", $outLink);

				$footer = new Template("footer.tpl");
				$footer->set("email", "");

				$layout = new Template("layout.tpl");
				$layout->set("header", $header->output());
				$layout->set("content", $content->output());
				$layout->set("footer", $footer->output());

				echo $layout->output();
			}		
		}
	}
	// Failed to move file to uploads/
	else
	{
		$header = new Template("header.tpl");
		$header->set("title", "Sierra to PeopleSoft");
		$header->set("heading", "Sierra to PeopleSoft");
		$header->set("subheading", "Error");

		$content = new Template("error.tpl");
		$content->set("heading", "Server Error");
		$content->set("command", "N/A"); 
		$content->set("stdout", "Failed to move file. Check permissions on upload directory.");

		$footer = new Template("footer.tpl");
		$footer->set("email", "");

		$layout = new Template("layout.tpl");
		$layout->set("header", $header->output());
		$layout->set("content", $content->output());
		$layout->set("footer", $footer->output());

		echo $layout->output();
	}

}
// If checkArgs() returns false 
else 
{
	$header = new Template("header.tpl");
	$header->set("title", "Sierra to PeopleSoft");
	$header->set("heading", "Sierra to PeopleSoft");
	$header->set("subheading", "Error");

	$content = new Template("error.tpl");
	$content->set("heading", "Input Error");
	$content->set("command", "N/A"); 
	$content->set("stdout", $errStr);

	$footer = new Template("footer.tpl");
	$footer->set("email", "");

	$layout = new Template("layout.tpl");
	$layout->set("header", $header->output());
	$layout->set("content", $content->output());
	$layout->set("footer", $footer->output());

	echo $layout->output();
}

?>






