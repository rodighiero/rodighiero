module Jekyll
  class FilterPageGenerator < Generator
    safe true

    def generate(site)
      filters = [
        { slug: 'books',             filter: 'book',       redirects: ['/Books'] },
        { slug: 'journal-articles',  filter: 'journal',    redirects: ['/Journal-Articles'] },
        { slug: 'conference-papers', filter: 'conference', redirects: [] },
        { slug: 'book-chapters',     filter: 'chapter',    redirects: [] },
        { slug: 'magazine-articles', filter: 'magazine',   redirects: [] },
        { slug: 'maps',              filter: 'map',        redirects: [] },
      ]
      filters.each do |f|
        site.pages << FilterPage.new(site, f[:slug], f[:filter], f[:redirects])
      end
    end
  end

  class FilterPage < PageWithoutAFile
    def initialize(site, slug, filter, redirects)
      super(site, site.source, slug, 'index.html')
      self.data = {
        'layout'        => 'home',
        'filter'        => filter,
        'redirect_from' => redirects,
      }
    end
  end
end
