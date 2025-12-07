#!/usr/bin/php
<?php
	// A simple script to turn cloudflare analytics URLs into expression rules suitable for blocking in the security rules section

	header("Content-Type: text/plain");

	// Copy and paste the filtering URL from https://dash.cloudflare.com/xxxxxxxxxxxxxxx/example.com/security/analytics
	$url = "https://dash.cloudflare.com/xxxxxxxxxxxxxxx/example.com/security/analytics/events?ip~neq=x.x.x.x&user-agent~neq=Dumb%20web%20spider&asn~neq=xxxxxxx&path~neq=%2Fsome%2Fwebsite%2Fpath&".
		"path~!starts=%2FSsome%2Fwebsite%2Fpath2&country~neq=BadCountryCode&path~!contains=BadPathOrFileName";

	$parts = parse_url($url);

	$params = proper_parse_str($parts['query']);

	if(isset($params["ip~neq"]))
	{
		$hasAnIP = false;
		echo "ip.src in {";
		if(is_array($params["ip~neq"]) && count($params["ip~neq"]) > 0)
		{
			foreach($params["ip~neq"] as $IP)
			{
				if($hasAnIP)
					echo " ";
				else
					$hasAnIP = true;

				echo $IP;
			}
		} else {
			if($params["ip~neq"] != "")
				echo $params["ip~neq"];
		}

		echo "}\n\n";
	}

	if(isset($params["asn~neq"]))
	{
		$hasAnASN = false;
		echo "ip.src.asnum in {";
		if(is_array($params["asn~neq"]) && count($params["asn~neq"]) > 0)
		{
			foreach($params["asn~neq"] as $ASN)
			{
				if($hasAnASN)
					echo " ";
				else
					$hasAnASN = true;

				echo $ASN;
			}
		} else {
			if($params["asn~neq"] != "")
				echo $params["asn~neq"];
		}

		echo "}\n\n";
	}

	if(isset($params["path~!contains"]))
	{
		if(is_array($params["path~!contains"]) && count($params["path~!contains"]) > 0)
			foreach($params["path~!contains"] as $path)
				echo " or (http.request.uri.path wildcard r\"*".$path."*\")";
		else
			if($params["path~!contains"] != "")
				echo " or (http.request.uri.path wildcard r\"*".$params["path~!contains"]."*\")";

		echo "\n\n";
	}

	if(isset($params["path~neq"]))
	{
		if(is_array($params["path~neq"]) && count($params["path~neq"]) > 0)
			foreach($params["path~neq"] as $path)
				echo " or (http.request.uri.path wildcard r\"".$path."*\")";
		else
			if($params["path~neq"] != "")
				echo " or (http.request.uri.path wildcard r\"".$params["path~neq"]."*\")";

		echo "\n\n";
	}

	if(isset($params["path~!starts"]))
	{
		if(is_array($params["path~!starts"]) && count($params["path~!starts"]) > 0)
			foreach($params["path~!starts"] as $path)
				echo " or (http.request.uri.path wildcard r\"".$path."*\")";
		else
			if($params["path~!starts"] != "")
				echo " or (http.request.uri.path wildcard r\"".$params["path~!starts"]."*\")";

		echo "\n\n";
	}

	if(isset($params["country~neq"]))
	{
		$hasAnCountry = false;
		echo "ip.src.country in {";
		if(is_array($params["country~neq"]) && count($params["country~neq"]) > 0)
		{
			foreach($params["country~neq"] as $country)
			{
				if($hasAnCountry)
					echo " ";
				else
					$hasAnCountry = true;

				echo "\"".$country."\"";;
			}
		} else {
			if($params["country~neq"] != "")
				echo "\"".$params["country~neq"]."\"";
		}

		echo "}\n\n";
	}

	// The following function came from the first comment by Evan K at https://www.php.net/parse_str
	function proper_parse_str($str)
	{
		// result array
		$arr = array();

		// split on outer delimiter
		$pairs = explode('&', $str);

		// loop through each pair
		foreach($pairs as $i)
		{
			// split into name and value
			list($name, $value) = explode('=', $i, 2);
			$value = rawurldecode($value);

			// if name already exists
			if(isset($arr[$name]))
			{
				// stick multiple values into an array
				if(is_array($arr[$name]))
					$arr[$name][] = $value;
				else
					$arr[$name] = array($arr[$name], $value);

				// otherwise, simply stick it in a scalar
			} else {
				$arr[$name] = $value;
			}
		}

		// return result array
		return $arr;
	}
