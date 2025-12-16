# Hugo와 Vercel로 블로그 만들고 배포하기

준비물:
- [Hugo](https://gohugo.io/)
- [Vercel](https://vercel.com)
- [Obsidian](https://obsidian.md/)

## 준비물 셋팅

macOS 기준으로 설명합니다.

### 1. Hugo
`Hugo`는 `Go`엔진으로 만들어진 오픈소스 정적 사이트 생성기다.

다양한 모듈, 테마 등을 제공하며,  
`md` 파일만 작성하면 `Hugo`가 이를 파싱해 블로그, 문서 사이트를 만들 수 있다.

Homebrew가 있는 경우,  
```shell
brew install hugo
hugo version 
```  
명령어로 설치할 수 있고, 추가적인 설정은 없다.

### 2. Vercel
`Vercel`은 `Github`등 레포지토리를 연결해 정적 사이트를 자동 빌드/배포해주는 플랫폼입니다. 

`Github` 계정으로 연동 로그인하면 이후 배포 연결이 편합니다. 

`cli`도 제공하지만, `Vercel`은 웹 페이지 UI가 잘 되어 있어 충분합니다.

### 3. Obsidian
`Obsidian`은 `Notion`과 비슷하게, 로컬 폴더를 기반으로 `md`문서를 관리하는 노트 앱입니다.  

보관함을 `Vault`로 명명하며, 이를 후술할 블로그 디렉토리 내에 생성하면 버전관리까지 하기 좋습니다. 


## Hugo 프로젝트 생성
`hugo new site {blog_name}` 명령어를 통해 해당 디렉토리 하위에 `{blog_name}` 폴더를 만들고, `hugo` 프로젝트가 생성된다. 

지금 `hugo server`를 통해 서버를 띄우면  
`1313`포트로 로컬에 서버가 올라가지만 **PAGE NOT FOUND** 만 보이는데,  
정상이다. 아직 테마가 없다. 테마를 찾으러 가면 된다.

## 테마 적용 
[Hugo Themes](https://themes.gohugo.io/)

여기에 블로그, 문서, 랜딩 페이지 등 다양한 테마들이 존재하고, 원하는 것을 선택하면 된다.

단, 테마마다 설정이 많이 다르기 떄문에, 이 글에선 내가 선택한 테마를 기준으로 설명하려고 한다. 

### Hugo Book 
[Hugo Book](https://themes.gohugo.io/themes/hugo-book/)

나는 docs에 사용할만한 테마를 사용해, 글을 작성하고 있다.  
용도나 사용 방식에 따라 원하는 것을 사용하면 되는데,  
거의 모든 테마는 다운로드를 누르면 `Github` 레포지토리로 이동하고,  
`README`를 보면 설치방법이 상세하게 나와있다. 

해당 테마에서는 2가지 적용법이 있다.  
1. submodule로 추가  
2. hugo module로 추가

나는 1번이 가장 간편해보여  
    `git submodule add https://github.com/alex-shpak/hugo-book themes/hugo-book`

명령어를 통해 서브모듈로 추가하고,
hugo 프로젝트 생성시 같이 생성된 `hugo.toml`파일에 
`theme = 'hugo-book'` 구문을 추가하여 기본테마를 설정해주었다.  

추가적으로 `title`, `baseURL` 뿐만 아니라 `ignoreFiles`, `params` 등을 해당 설정 파일에서 수정하거나 추가할 수 있다. 

## 글 작성

글 작성도 두 가지 방법이 있다.  
1. `Hugo` 명령어: `hugo new content {example.md}`    
2. `obsidian` Templater를 통한 템플릿 생성

위에서 옵시디언을 준비했으므로, 2번을 선택해서 하도록 한다. 

옵시디언 초기 설정이나, 메뉴바의 `File/Open Vault`를 통해 새로운 Vault나 이미 생성된 폴더를 Vault로 사용할 수 있다.

만들어진 `Hugo`프로젝트 내 `/content/`, 또는 `/content/{post}` 등으로 vault를 설정하면 된다. 

이제 옵시디언에 글을 쓰면 md파일로 저장되고, 이를 커밋하면 Vercel이 후킹해서 자동으로 배포되는 구조를 만들 수 있다. 

### Templater

하단 톱니바퀴 또는 메뉴바의 `Obsidian/Preferences`를 클릭하면 설정창을 볼 수 있다.

여기서 `Options` 카테고리의 `Community plugins`에서 `Browse`를 클릭하면 유저가 만든 플러그인들을 다운받을 수 있다.

`Templater`를 검색하고, 다운받으면 된다. 

이를 활성화하고, 템플릿을 등록하고 이를 생성시마다 자동 적용되도록 설정하면 끝이다.

1. Template folder location 설정  
    템플릿을 담고 있는 폴더를 따로 만들면 된다.  
    나는 내부에 `_templates`라는 별도의 폴더를 생성해서 템플릿을 담아두었다.
2. Trigger Templater on new file creation 활성화  
    파일 생성 시 특정한 조건에 따라 자동으로 템플릿이 적용되도록 설정할 수 있다.
3. Enable folder templates 활성화  
    활성화 후, `folder`에는 트리거를 적용할 폴더, `template`에는 적용할 템플릿을 설정한다.  
    나는 전역 템플릿 하나만 사용하고 있으므로,  
    `folder: /, template: _templates/global.md`를 설정했다. 
    물론 `global.md`도 만들어야 한다.

### global.md
```md
<%*
  let title = tp.file.title;

  if (title.startsWith("Untitled")) {
    title = await tp.system.prompt("제목을 입력해주세요");

    if (!title || title.trim() === "") {
      const file = tp.file.find_tfile(tp.file.path(true));
      await app.vault.trash(file, false);
      return;
    }

    await tp.file.rename(title);
  }

  const slug = title
    .toLowerCase()
    .replace(/\s+/g, '-')
    .replace(/[^a-z0-9\-]/g, '');

  const nowISO  = tp.date.now("YYYY-MM-DDTHH:mm:ssZ");
  const created = tp.date.now("YYYY-MM-DD");
  const updated = tp.file.last_modified_date("YYYY-MM-DD");

  tR += `---
title: "${title}"
date: ${nowISO}
draft: true
slug: "${slug}"
tags: []
categories: []
summary: ""
weight: 1
bookHidden: false
---
# **${title}**
`;
%>
```

위의 템플릿을 사용해 생성하면 새로운 파일을 만들 때 제목을 설정하는 창이 뜨고, title, date, slug, tags, 등을 적용하는 Properties를 자동으로 생성해준다.

### _index.md

해당 파일로 만들면, 해당 폴더의 대문으로 설정된다.  
그래서 `content`의 `_index.md`는 블로그의 대문이 된다.

Obsidian 템플릿을 통해 생성했다.

## 배포

`Vercel`에 `Hugo` 배포 옵션이 있어, 간단하게 배포할 수 있다.

단, Vercel의 Hugo 기본 버전이  
2025-12-15 기준 0.58.0버전으로 설정되어 있었는데,  
해당 테마의 경우 해당 버전에서 수식 설정 등에 문제가 발생하는 경우가 있었다.


이 경우 환경 변수에서 
`HUGO_VERSION = 0.151.0`을 설정해주면 된다.

### 빌드 순서

1.	GitHub에 Hugo 프로젝트를 푸시  
    public/은 커밋하지 않는다. (Vercel이 빌드해서 생성)
2.	Vercel 대시보드 → New Project → Import Git Repository  
    배포 옵션은 Hugo 선택

3. 생성된 배포 URL 확인

## 결론

이전의 블로그는 `next.js` 기반 템플릿을 사용하고 있었는데, 최근 취약점 문제와 함께 버전 꼬임 문제로 블로그를 내렸었다.

이 때문에 좀 더 가볍고 간단한 정적 사이트 생성기를 원했고, `hugo` 가 적절한 선택이라 생각했다.

블로그는 만들기 쉽다. 관리가 어려워서 그렇지