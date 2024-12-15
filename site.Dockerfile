# See
#    https://docs.github.com/en/pages/setting-up-a-github-pages-site-with-jekyll
#    https://github.com/BillRaymond/my-jekyll-docker-website

# As of 2024-12-15, Github pages require Ruby 3.3.4 and Jekyll 3.10.0
# see https://pages.github.com/versions/
FROM ruby:3.3-alpine

# Add Jekyll build dependencies to Alpine
RUN apk update
RUN apk add --no-cache build-base gcc cmake git

# Update the Ruby bundler and install Jekyll,
# pin dependency versions to avoid conflicts
RUN gem install bundler -v 2.5.23
RUN gem install ffi     -v 1.17.0
RUN gem install jekyll  -v 3.10.0


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
#CMD bundle exec jekyll serve --host 0.0.0.0
