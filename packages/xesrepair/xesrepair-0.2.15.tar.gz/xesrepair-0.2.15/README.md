# 每次发版注意事项
1. 修改setup.py中的版本信息
2. 运行python setup.py sdist bdist_wheel进行打包
3. 上传pypi
   ### 1、pypi账号：zhushaodong123 密码：R4E3W2Q1zxc
   2FA二次验证码
    184cb984cb0c8998
    21a96d0d4a56b7a5
    7d450bb521ff574f
    11c50a829a9aca1e
    7c1e628bf3a7fec9
    4222a05c0dc3e843
    6c5a12ccd5fcf68e
    75caa7f8a531be11

   谷歌动态二次验证:手机下载Google Authenticator


   ### 2、执行打包上传命令
    1、打包,生成对应版本的好的.gz文件: 
    mac运行：python3 setup.py sdist bdist_wheel 
    windows运行：python setup.py sdist bdist_wheel

    2、在 ~/.pypirc,配置

    [distutils]
    index-servers = pypi

    [pypi]
    username:__token__
    password:pypi-AgEIcHlwaS5vcmcCJGZkYTAyY2RiLWQ2ZmUtNGM4ZC1hZGJlLWU1MGQ2ZWVjYTI3ZgACKlszLCJlZDJmYTA1My0wYmU2LTRlYzEtYjYwNy05OWI1ZmNjNmNlYjciXQAABiDqeKB2lUYsJQBXCysTnoP3p_aFjuTxR7n-aYKcd_zNfQ

    3、上传到pypi官网,
      twine upload dist/xxx.gz
      xxx.gz是上一步打包生成的文件,上一步加bdist_wheel参数后,兼容性更好,需要把生成的whl文件也一起上传twine upload dist/xxx.gz,可能会失败,多试几次。参考文档:https://pypi.org/project/twine/
   

