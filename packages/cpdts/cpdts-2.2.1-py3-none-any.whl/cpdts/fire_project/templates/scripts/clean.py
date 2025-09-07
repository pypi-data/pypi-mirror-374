

# 实现 clean_dist 函数用来清理dist 文件夹 
import os
def main():
    dist_path = os.path.join(os.getcwd(), 'dist')
    if os.path.exists(dist_path):
        for root, dirs, files in os.walk(dist_path, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(dist_path)
    else:
        print('dist文件夹不存在')


if __name__ == '__main__':
    main()
