# Emits one redirect stub page per alias — driven by the `redirect_from` front-matter
# key on any page or document. Introduces no identifier a template can read.
#
# Generates a small redirect stub for every alias listed in a page's or
# document's `redirect_from` front matter, so shortened or retired URLs keep
# resolving to the canonical page. Local replacement for jekyll-redirect-from,
# with no external gem.
# Site migration aliases live in _data/legacy_redirects.yml, keeping restored
# historical routes separate from publications' content modification dates.
#
# The stub carries rel=canonical and deliberately no `noindex`. The two are
# contradictory instructions — Google resolves the conflict by picking the
# canonical — so the tag only argued with the line beneath it. What keeps an
# alias out of the index is the instant refresh, which a crawler follows to the
# real page; the canonical then hands that page credit for whatever links the
# alias earned, which a noindex would throw away instead.
#
#   redirect_from: /surprise-machines
#   redirect_from:
#     - /Surprise-Machines
#     - /old/path/
#
# An alias without an extension is written as `<alias>.html` (served at the
# extensionless URL by both GitHub Pages and `jekyll serve`); one ending in a
# slash is written as `<alias>/index.html`.
require 'cgi'
require 'json'
require 'uri'

module Jekyll
  class RedirectPage < PageWithoutAFile
    def initialize(site, dir, name, target, canonical)
      super(site, site.source, dir, name)

      # No front matter to carry: the stub renders with no layout, sitemap.xml walks
      # site.publications rather than site.pages, and the target below is interpolated
      # into the markup rather than read back off the page.
      self.data = {}
      target_attr = CGI.escapeHTML(target)
      self.content = <<~HTML
        <!DOCTYPE html>
        <html lang="en">
        <head>
          <meta charset="utf-8">
          <title>Redirecting…</title>
          <link rel="canonical" href="#{CGI.escapeHTML(canonical)}">
          <meta http-equiv="refresh" content="0; url=#{target_attr}">
          <script>location.replace(#{JSON.generate(target)});</script>
        </head>
        <body>
          <p>Redirecting to <a href="#{target_attr}">#{target_attr}</a>…</p>
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
      items = site.pages + site.documents
      real_paths = items.map(&:url)
      occupied = real_paths.map { |path| split_path(path) }

      items.each do |item|
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
          if occupied.include?([dir, name])
            raise Jekyll::Errors::FatalException, "publication_redirect: alias '#{alias_path}' would overwrite a real page"
          end
          occupied << [dir, name]
          site.pages << RedirectPage.new(site, dir, name, target, canonical)
        end
      end

      (site.data['legacy_redirects'] || {}).each do |alias_path, destination|
        uri = URI.parse(destination)
        unless alias_path.start_with?('/') && !alias_path.start_with?('//') &&
               uri.host.nil? && uri.scheme.nil? && real_paths.include?(uri.path)
          raise Jekyll::Errors::FatalException, "publication_redirect: invalid migration alias #{alias_path.inspect} -> #{destination.inspect}"
        end
        dir, name = split_path(alias_path)
        if seen.key?(alias_path) || occupied.include?([dir, name])
          raise Jekyll::Errors::FatalException, "publication_redirect: migration alias '#{alias_path}' duplicates an existing page or alias"
        end
        occupied << [dir, name]
        target = "#{site.baseurl}#{destination}"
        canonical = "#{site.config['url']}#{site.baseurl}#{uri.path}"
        site.pages << RedirectPage.new(site, dir, name, target, canonical)
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
