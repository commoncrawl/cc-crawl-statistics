# See
#    https://docs.github.com/en/pages/setting-up-a-github-pages-site-with-jekyll
#    https://github.com/BillRaymond/my-jekyll-docker-website

# As of 2024-06-04, Github pages require Ruby 2.7.4 and Jekyll 3.9.5
# see https://pages.github.com/versions/
FROM ruby:2.7-alpine3.16

# Add Jekyll build dependencies to Alpine
RUN apk update
RUN apk add --no-cache build-base gcc cmake git

# Update the Ruby bundler and install Jekyll,
# pin dependency versions to avoid conflicts
RUN gem install bundler -v 2.4.22
RUN gem install ffi     -v 1.16.3
RUN gem install jekyll  -v 3.9.5


RUN mkdir /cc-crawl-statistics
WORKDIR /cc-crawl-statistics

RUN echo -e "source 'https://rubygems.org'\ngem 'github-pages', group: :jekyll_plugins" >Gemfile
RUN bundle install
RUN bundle exec jekyll clean

COPY index.md _config.yml ./
COPY _layouts/ ./_layouts/
COPY assets/ ./assets/
COPY plots/ ./plots/

CMD bundle exec jekyll serve
