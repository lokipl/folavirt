function createApplet(width, height, address, port, newwindow, tmppasswd, scalingfactor){
	var code = '<applet id="vncapplet" archive="/applets/TightVncViewer.jar" code="com.tightvnc.vncviewer.VncViewer"';
	code += 'width="' + width + '" height="' + height + '">';
	code += '<param name="HOST" value="' + address + '">';
	code += '<param name="PORT" value="' + port +'">';
	
	if (scalingfactor) code += '<param name="Scaling factor" value="auto">';
	if (newwindow) code += '<param name="Open new window" value="Yes">';	
	if (tmppasswd != '') code += '<param name="PASSWORD" value="' + tmppasswd +'">';	
	
	code += '</applet>';
	return code;
}