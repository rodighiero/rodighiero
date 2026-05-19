Jekyll::Hooks.register :site, :after_init do |site|
  readme_path = File.join(site.source, 'README.md')
  site.config['readme_content'] = File.read(readme_path) if File.exist?(readme_path)
end
