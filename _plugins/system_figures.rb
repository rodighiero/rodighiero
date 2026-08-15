# Attaches the `figures` field to each publication (read by sitemap.xml:16).
#
# Collects the images that actually appear inside a publication's body — the
# figures rendered by figure-single.html / figure-group.html — and exposes them
# as `figures`, a list of site-absolute paths ("/images/slug/fig_001.webp").
#
# This is what sitemap.xml declares per publication: what the page actually
# shows. Every source image now lives in its publication's own images/<slug>/
# folder, so a body figure is declared whether it is a numbered figure or the
# cover.webp that an abstract-only entry opens on — in both cases the reader
# sees it. images/@cards/ is excluded because it is not a source at all: it
# holds the downsized copies generate-thumbnails.py bakes for the homepage
# gallery, which no article body has reason to reference.
#
# The two includes take their paths differently, so both are normalised to a
# site-absolute path: figure-single takes an already-absolute src="/images/…",
# figure-group a pipe-delimited images="slug/a.webp|slug/b.webp" that the
# include prefixes itself.
class Jekyll::PublicationFiguresGenerator < Jekyll::Generator
  priority :high

  # Non-greedy up to the first "%}" so a caption containing "%" can't swallow
  # the rest of the file.
  SINGLE = %r!\{%\s*include\s+figure-single\.html\b(.*?)%\}!m
  GROUP  = %r!\{%\s*include\s+figure-group\.html\b(.*?)%\}!m

  # Generated homepage gallery copies, never declared as article imagery.
  EXCLUDED = "/images/@cards/".freeze

  def generate(site)
    docs = site.collections['publications']&.docs
    return unless docs

    docs.each do |doc|
      paths = []
      # Generators run before rendering, so doc.content is still the raw source.
      doc.content.scan(SINGLE) { |(args)| paths << args[/src="([^"]*)"/, 1] }
      doc.content.scan(GROUP)  { |(args)| paths.concat(args[/images="([^"]*)"/, 1].to_s.split("|")) }

      doc.data["figures"] = paths.compact
                                 .map { |path| absolute(path) }
                                 .uniq
                                 .reject { |path| path.start_with?(EXCLUDED) }
                                 .select { |path| present?(site, doc, path) }
    end
  end

  private

  def absolute(path)
    path = path.strip
    path.start_with?("/") ? path : "/images/#{path}"
  end

  # Keeping a missing file out of the sitemap matters more than listing it:
  # a 404 in an image sitemap is a crawl error rather than a discovered image.
  def present?(site, doc, path)
    return true if File.exist?(File.join(site.source, path))

    Jekyll.logger.warn 'system_figures:', "#{doc.relative_path} references missing image #{path}"
    false
  end
end
