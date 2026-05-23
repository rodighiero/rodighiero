# Sets page.date from page.year for publications, preserving the homepage
# sort order (year desc, then alphabetical within each year) in the feed.
# Within a year, alphabetically-first titles get a slightly later timestamp
# so they appear first in the feed (which sorts newest-first).
class PublicationDateGenerator < Jekyll::Generator
  priority :high

  def generate(site)
    docs = site.collections['publications']&.docs
    return unless docs

    docs.group_by { |doc| doc.data['year'].to_i }.each do |year, group|
      sorted = group.sort_by { |doc| doc.data['title'].to_s.downcase }
      sorted.each_with_index do |doc, i|
        doc.data['date'] = Time.new(year, 1, 1, 23, 59, sorted.size - 1 - i)
      end
    end
  end
end
