# site.data.network_client — read by home.html's #net-data script tag.
#
# The browser's share of _data/network.json, and only that. The file on disk is
# read by three surfaces with three different appetites: publication.html walks
# `nodes[].related` for its "Related publications" list, home.html's Liquid
# builds the cluster cards from `clusters` and quotes `params` in the network
# legend — both at build time — while the network view's JavaScript needs a much
# smaller thing at run time. Inlining the whole file served the third from the
# union of all three, and every visitor paid for it in the homepage's HTML,
# including the majority who never open the network view.
#
# So this projects out exactly what the JS reads, established by grepping the
# module rather than by guessing:
#
#   nodes[]  slug, title, url, x, y, tr?, related[]{slug, sim}
#   links[]  source, target, fb?
#   canvas, params
#
# What it drops, and why each is safe:
#
#   clusters            no JS touches it; the cluster cards are rendered
#                       server-side and carry their own data-slugs
#   related[].title     the panel maps r.slug to a node index and reads the
#   related[].url       title and url off `nodes`, so these are the same
#   related[].lang      strings a second time — the bulk of the saving
#   nodes[].i           the array position, which the JS re-derives anyway
#   nodes[].lang        unread in the browser
#   links[].value       unread; edges are drawn straight, at one weight
#
# `tr` and `fb` are omitted where false rather than written as false: the JS
# reads both through !!, so absence and false are the same value to it.
#
# If the view ever needs another field, add it here — not by falling back to
# inlining the whole file, which is the state this replaced.
class Jekyll::NetworkClientGenerator < Jekyll::Generator
  priority :high
  safe true

  def generate(site)
    net = site.data['network']
    unless net.is_a?(Hash) && net['nodes'].is_a?(Array) && net['links'].is_a?(Array)
      Jekyll.logger.warn 'system_network_client:',
                         '_data/network.json missing or malformed — the network view will not render'
      return
    end

    site.data['network_client'] = {
      'nodes'  => net['nodes'].map { |n| node_for(n) },
      'links'  => net['links'].map { |l| link_for(l) },
      'canvas' => net['canvas'],
      'params' => net['params'],
    }
  end

  private

  def node_for(node)
    out = {
      'slug'  => node['slug'],
      'title' => node['title'],
      'url'   => node['url'],
      'x'     => node['x'],
      'y'     => node['y'],
    }
    out['tr'] = true if node['tr']
    related = (node['related'] || []).map { |r| { 'slug' => r['slug'], 'sim' => r['sim'] } }
    out['related'] = related unless related.empty?
    out
  end

  def link_for(link)
    out = { 'source' => link['source'], 'target' => link['target'] }
    out['fb'] = true if link['fb']
    out
  end
end
