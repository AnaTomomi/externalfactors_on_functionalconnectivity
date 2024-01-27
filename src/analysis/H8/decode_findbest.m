function success = decode_findbest(data)
    if(size(data,1) ~= size(data,2))
        error('similarity matrix is not square')
    end
    [x y]=ind2sub(size(data),find(max(data)==data));
    v = x==y;
    success = mean(v);
    

