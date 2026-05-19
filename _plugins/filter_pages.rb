module Jekyll
  class FilterPageGenerator < Generator
    safe true

    FILTERS = [
      { slug: 'books',             filter: 'book',       redirects: ['/Books'] },
      { slug: 'journal-articles',  filter: 'journal',    redirects: ['/Journal-Articles'] },
      { slug: 'conference-papers', filter: 'conference', redirects: [] },
      { slug: 'book-chapters',     filter: 'chapter',    redirects: [] },
      { slug: 'magazine-articles', filter: 'magazine',   redirects: [] },
      { slug: 'maps',              filter: 'map',        redirects: [] },
    ]

    def generate(site)
      FILTERS.each do |f|
        site.pages << FilterPage.new(site, f[:slug], f[:filter], f[:redirects])
      end
    end
  end

  class FilterPage < Page
    def initialize(site, slug, filter, redirects)
      @site    = site
      @base    = site.source
      @dir     = slug
      @name    = 'index.html'
      self.process(@name)
      self.content = ''
      self.data = {
        'layout'        => 'home',
        'filter'        => filter,
        'redirect_from' => redirects,
      }
    end
  end
end
