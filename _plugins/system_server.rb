# | Cache-Control: no-store on every response of the local `jekyll serve` — read by the browser.
#
# Live editing replaces images under the same URL. WEBrick sends no Cache-Control,
# so the browser falls back to heuristic caching: an image unchanged for months is
# judged fresh for days, and figures are loading="lazy", so they load after a hard
# reload has already finished and come straight back from the stale cache.
#
# `webrick: headers:` in _config.yml cannot fix this: with livereload on, Jekyll's
# servlet returns early for anything that is not HTML, before merging those headers.
# So the servlet is wrapped instead, and the header set on every response.
#
# Development only. The hook fires only when the site is being served (Jekyll sets
# config["serving"]), so `jekyll build` and the deploy never load WEBrick or this
# patch, and the published site's caching is untouched.
Jekyll::Hooks.register :site, :after_init do |site|
  next unless site.config['serving']
  next if defined?(Jekyll::NoStoreServlet)

  require 'jekyll/commands/serve/servlet'

  module Jekyll::NoStoreServlet
    def do_GET(req, res) # rubocop:disable Naming/MethodName
      rtn = super
      res['Cache-Control'] = 'no-store'
      rtn
    end
  end

  Jekyll::Commands::Serve::Servlet.prepend(Jekyll::NoStoreServlet)
  Jekyll.logger.info 'system_server:', 'Cache-Control: no-store on every served file'
end
