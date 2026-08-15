# site.data.readme_content — README.md read whole, split into the three bio
# paragraphs by home.html. Lets README.md double as the GitHub repo readme.
Jekyll::Hooks.register :site, :post_read do |site|
  readme_path = File.join(site.source, 'README.md')
  if File.exist?(readme_path)
    site.data['readme_content'] = File.read(readme_path)
  else
    Jekyll.logger.warn 'system_readme:', 'README.md not found — bio will be empty'
  end
end
