Jekyll::Hooks.register :site, :post_read do |site|
  readme_path = File.join(site.source, 'README.md')
  if File.exist?(readme_path)
    site.data['readme_content'] = File.read(readme_path)
  else
    Jekyll.logger.warn 'readme_content:', 'README.md not found — bio will be empty'
  end
end
