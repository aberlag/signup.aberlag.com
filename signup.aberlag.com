# Nginx config for signup.aberlag.com

# Requires an apache password file
# http://httpd.apache.org/docs/2.2/programs/htpasswd.html

server {
        listen   80;
        server_name signup.aberlag.com;
        location / {
                auth_basic "This site is restricted";
                auth_basic_user_file '/var/www/aberlag.com/signup_auth';
                proxy_pass http://localhost:5000;
                proxy_set_header Host $host;
                proxy_set_header X-Real-IP $remote_addr;
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }
}
