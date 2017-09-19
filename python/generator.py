for x in range(1,24):
	
	print "var lakon%s = d3.svg.line().x(function(d) { return x(d.number);}).y(function(d) {if (d.lakon%s !== | d.number<8){return y(d.lakon%s);}});" %(x,x,x)
	#print "var lakon%s = d3.svg.line().x(function(d) { return x(d.number);}).y(function(d) {return y(d.lakon%s);});" %(x,x)
	
	#print 'svg.append("path").attr("class", "lakonLine").attr("id", "lakon%s").attr("d", lakon%s(data));' % (x,x)
