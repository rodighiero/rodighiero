# Sets page.date from page.year for publications.
# Runs as a Generator (before jekyll-feed collects dates) so the feed
# uses the actual publication year rather than the build date.
class PublicationDateGenerator < Jekyll::Generator
  priority :high

  def generate(site)
    site.collections['publications']&.docs&.each do |doc|
      doc.data['date'] = Time.new(doc.data['year'].to_i, 1, 1) if doc.data['year']
    end
  end
end
