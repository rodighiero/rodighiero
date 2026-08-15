# Emits one redirect stub page per alias — driven by the `redirect_from` front-matter
# key on any page or document. Introduces no identifier a template can read.
#
# Generates a small redirect stub for every alias listed in a page's or
# document's `redirect_from` front matter, so shortened or retired URLs keep
# resolving to the canonical page. Local replacement for jekyll-redirect-from,
# with no external gem.
#
#   redirect_from: /surprise-machines
#   redirect_from:
#     - /Surprise-Machines
#     - /old/path/
#
# An alias without an extension is written as `<alias>.html` (served at the
# extensionless URL by both GitHub Pages and `jekyll serve`); one ending in a
# slash is written as `<alias>/index.html`.
module Jekyll
  class RedirectPage < PageWithoutAFile
    def initialize(site, dir, name, target, canonical)
      super(site, site.source, dir, name)

      self.data = {
        "layout"   => nil,
        "sitemap"  => false,
        "target"   => target,
      }
      self.content = <<~HTML
        <!DOCTYPE html>
        <html lang="en">
        <head>
          <meta charset="utf-8">
          <title>Redirecting…</title>
          <meta name="robots" content="noindex">
          <link rel="canonical" href="#{canonical}">
          <meta http-equiv="refresh" content="0; url=#{target}">
          <script>location.replace("#{target}");</script>
        </head>
        <body>
          <p>Redirecting to <a href="#{target}">#{target}</a>…</p>
        </body>
        </html>
      HTML
    end
  end

  class RedirectGenerator < Generator
    safe true
    priority :low

    def generate(site)
      seen = {}

      (site.pages + site.documents).each do |item|
        Array(item.data["redirect_from"]).each do |alias_path|
          alias_path = alias_path.to_s.strip
          next if alias_path.empty?

          unless alias_path.start_with?("/")
            Jekyll.logger.warn 'publication_redirect:', "#{item.relative_path}: redirect_from '#{alias_path}' must start with '/', skipped"
            next
          end

          if seen.key?(alias_path)
            Jekyll.logger.warn 'publication_redirect:', "#{item.relative_path}: redirect_from '#{alias_path}' already claimed by #{seen[alias_path]}, skipped"
            next
          end
          seen[alias_path] = item.relative_path

          target    = File.join(site.baseurl.to_s, item.url)   # relative: works locally and in production
          canonical = "#{site.config['url']}#{target}"         # absolute: what search engines should keep
          dir, name = split_path(alias_path)
          site.pages << RedirectPage.new(site, dir, name, target, canonical)
        end
      end
    end

    private

    # "/surprise-machines" -> ["/", "surprise-machines.html"]
    # "/old/path/"         -> ["/old/path", "index.html"]
    def split_path(alias_path)
      if alias_path.end_with?("/")
        [alias_path.chomp("/"), "index.html"]
      else
        dir  = File.dirname(alias_path)
        base = File.basename(alias_path)
        base += ".html" if File.extname(base).empty?
        [dir, base]
      end
    end
  end
end
