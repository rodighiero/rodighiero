# Liquid filter exposing an image's intrinsic pixel dimensions at build time,
# so figure markup can set width/height and avoid layout shift (CLS).
# Pure-Ruby WebP parser (VP8/VP8L/VP8X) — no ImageMagick/gem dependency.
# Usage: {% assign d = src | image_size %}{{ d.width }}×{{ d.height }}
module Jekyll
  module ImageSizeFilter
    def image_size(src)
      return empty_dims if src.nil? || src.empty?
      site = @context.registers[:site]
      path = File.join(site.source, src.sub(%r{\A/}, ''))
      ImageSizeFilter.cache[path] ||= ImageSizeFilter.read(path) || empty_dims
    end

    def empty_dims
      { 'width' => nil, 'height' => nil }
    end

    def self.cache
      @cache ||= {}
    end

    def self.clear_cache
      @cache = {}
    end

    def self.read(path)
      return nil unless File.file?(path)
      File.open(path, 'rb') { |f| parse(f) }
    rescue StandardError
      nil
    end

    def self.parse(f)
      header = f.read(12)
      return nil unless header && header.byteslice(0, 4) == 'RIFF' && header.byteslice(8, 4) == 'WEBP'
      tag = f.read(4)
      f.read(4) # chunk size (unused)
      case tag
      when 'VP8 '
        b = f.read(10).bytes
        { 'width' => ((b[7] << 8 | b[6]) & 0x3fff), 'height' => ((b[9] << 8 | b[8]) & 0x3fff) }
      when 'VP8L'
        b = f.read(5).bytes # b[0] is the 0x2f signature
        { 'width'  => (((b[2] & 0x3f) << 8 | b[1]) + 1),
          'height' => (((b[4] & 0x0f) << 10 | b[3] << 2 | (b[2] & 0xc0) >> 6) + 1) }
      when 'VP8X'
        b = f.read(10).bytes
        { 'width'  => ((b[6] << 16 | b[5] << 8 | b[4]) + 1),
          'height' => ((b[9] << 16 | b[8] << 8 | b[7]) + 1) }
      end
    end
  end
end

Liquid::Template.register_filter(Jekyll::ImageSizeFilter)

# Clear cache at the start of each build to prevent memory leaks in long-running
# jekyll serve sessions. Also ensures deleted images don't return stale cached data.
Jekyll::Hooks.register :site, :pre_render do |site|
  Jekyll::ImageSizeFilter.clear_cache
end
