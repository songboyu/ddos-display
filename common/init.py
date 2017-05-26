from tornado import web


class WiseHandler(web.RequestHandler):
	@property
	def http_host(self):
		return self.request.host
	
	def compute_etag(self):
		return None
	
	def get_error_html(self, status_code, **kwargs):
		if status_code == 403:
			return self.render_string("403.html")
		elif status_code == 404:
			return self.render_string("404.html")
		elif status_code == 405:
			return self.render_string("405.html")
		elif status_code == 500:
			return self.render_string("500.html")
		else:
			return self.render_string("error.html")


class PageNotFound(web.RequestHandler):
	def get(self):
		self.set_status(404)
		self.render("404.html")
	
