function addZerobefore(number) {
	if(parseInt(number) < 10 && parseInt(number) > -10) {
		number = "0" + parseInt(number);
	}
	return number;
}