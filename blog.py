import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.autoreload
import json
import jsontemplate

long_poll_requests = []
posts = []

def add_post(title, body): posts.append({'title': title, 'body': body, 'id': len(posts)})

add_post('What my cat ate for breakfast', 'Cornflakes and toast')
add_post('Look mom, I am blogging', 'Hey everbody look at me')

class BlogPostsHandler(tornado.web.RequestHandler):
    def get(self):
        show_id = self.get_argument("show", None)
        if show_id:
            self.render("post.html", post=posts[int(show_id)])
            return
        
        content = jsontemplate.expand(open("posts_partial.html").read(), {'posts': posts})
        self.write(jsontemplate.expand(open("posts_json.html").read(), {'content': content}))

    def post(self):
        global long_poll_requests
        add_post(self.get_argument('title'), self.get_argument('body'))
        
        for x in long_poll_requests:
            x.on_finish({'posts': posts})
        long_poll_requests = []
        self.redirect("/posts")

class LongPollHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        long_poll_requests.append(self)

    def on_finish(self, data):
        self.write(json.dumps(data))
        self.finish()

settings = {"static_path": "."}

application = tornado.web.Application([
    (r"/posts", BlogPostsHandler),
    (r"/longpoll", LongPollHandler),
], **settings)

if __name__ == "__main__":
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8888)
    tornado.autoreload.start()
    tornado.ioloop.IOLoop.instance().start()
