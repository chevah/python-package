find ./ -type f \( -name "python" -o -name "*.so" \) -exec ldd {} + \
    | grep -v ^\\./ | awk '{print $1}' | sort | uniq | sort
