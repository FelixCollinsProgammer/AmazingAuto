#!/usr/bin/env python3

import os
import json
import yaml
import argparse
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any

class ProjectDetector:
    
    def __init__(self):
        pass
    
    def detect(self, project_path: str) -> Dict[str, Any]:
        project_info = {
            'path': project_path,
            'language': 'unknown',
            'framework': 'unknown',
            'structure': 'unknown',
            'complexity': 'low',
            'dependencies': [],
            'testing': False,
            'build_tools': [],
            'deployment': []
        }

        try:
            package_json = self._read_package_json(project_path)
            requirements_txt = self._read_requirements_txt(project_path)
            pom_xml = self._read_pom_xml(project_path)
            go_mod = self._read_go_mod(project_path)
            composer_json = self._read_composer_json(project_path)
            csproj = self._read_csproj(project_path)

            detection = self._detect_language_and_framework(project_path, {
                'package_json': package_json,
                'requirements_txt': requirements_txt,
                'pom_xml': pom_xml,
                'go_mod': go_mod,
                'composer_json': composer_json,
                'csproj': csproj
            })

            project_info.update(detection)
            project_info['structure'] = self._analyze_structure(project_path, project_info['language'])
            project_info['complexity'] = self._assess_complexity(project_info)
            project_info['testing'] = self._detect_testing(project_path, project_info['language'])
            project_info['build_tools'] = self._detect_build_tools(project_path, project_info)
            project_info['deployment'] = self._detect_deployment(project_path, project_info)

            return project_info

        except Exception as error:
            print(f"Ошибка при детекции проекта: {error}")
            raise error

    def _detect_language_and_framework(self, project_path: str, files: Dict) -> Dict[str, Any]:
        if files['package_json']:
            dependencies = files['package_json'].get('dependencies', {})
            dev_dependencies = files['package_json'].get('devDependencies', {})
            all_deps = {**dependencies, **dev_dependencies}
            
            if 'typescript' in all_deps or 'ts-node' in all_deps:
                return {
                    'language': 'typescript',
                    'framework': 'typescript',
                    'type': 'backend'
                }
            
            if 'react-native' in all_deps:
                return {
                    'language': 'javascript',
                    'framework': 'react-native',
                    'type': 'mobile'
                }
            
            if 'react' in all_deps or 'react-dom' in all_deps:
                return {
                    'language': 'javascript',
                    'framework': 'react',
                    'type': 'frontend'
                }
            
            if 'vue' in all_deps or '@vue/cli-service' in all_deps:
                return {
                    'language': 'javascript',
                    'framework': 'vue',
                    'type': 'frontend'
                }
            
            if '@angular/core' in all_deps or '@angular/cli' in all_deps:
                return {
                    'language': 'typescript',
                    'framework': 'angular',
                    'type': 'frontend'
                }
            
            if any(dep in all_deps for dep in ['express', 'koa', 'fastify', 'nestjs']):
                return {
                    'language': 'javascript',
                    'framework': 'nodejs',
                    'type': 'backend'
                }
            
            if files['package_json'].get('name') == 'express' or 'express' in files['package_json'].get('keywords', []):
                return {
                    'language': 'javascript',
                    'framework': 'express',
                    'type': 'backend'
                }
        
        if files['requirements_txt'] or self._file_exists(project_path, 'requirements.txt') or self._file_exists(project_path, 'pyproject.toml'):
            return {
                'language': 'python',
                'framework': self._detect_python_framework(project_path),
                'type': 'backend'
            }
        
        if files['pom_xml'] or self._file_exists(project_path, 'pom.xml') or self._file_exists(project_path, 'build.gradle'):
            return {
                'language': 'java',
                'framework': self._detect_java_framework(project_path),
                'type': 'backend'
            }
        
        if files['go_mod'] or self._file_exists(project_path, 'go.mod'):
            return {
                'language': 'go',
                'framework': self._detect_go_framework(project_path),
                'type': 'backend'
            }
        
        if (self._file_exists(project_path, 'Makefile') or 
            self._file_exists(project_path, 'CMakeLists.txt') or
            self._file_exists(project_path, 'configure') or
            self._file_exists(project_path, '*.c') or
            self._file_exists(project_path, '*.h')):
            return {
                'language': 'c',
                'framework': 'unknown',
                'type': 'backend'
            }
        
        if files['csproj'] or self._file_exists(project_path, '*.csproj'):
            return {
                'language': 'csharp',
                'framework': self._detect_csharp_framework(project_path),
                'type': 'backend'
            }
        
        if files['composer_json'] or self._file_exists(project_path, 'composer.json'):
            return {
                'language': 'php',
                'framework': self._detect_php_framework(project_path),
                'type': 'backend'
            }
        
        return {
            'language': 'unknown',
            'framework': None,
            'type': 'unknown'
        }
    
    def _analyze_structure(self, project_path: str, language: str) -> str:
        structure = {
            'monorepo': False,
            'microservices': False,
            'layered': False,
            'modular': False,
            'dockerized': False
        }
        
        if (self._file_exists(project_path, 'lerna.json') or 
            self._file_exists(project_path, 'nx.json') or
            self._file_exists(project_path, 'rush.json')):
            structure['monorepo'] = True
        
        if (self._file_exists(project_path, 'services') or 
            self._file_exists(project_path, 'microservices')):
            structure['microservices'] = True
        
        if (self._file_exists(project_path, 'Dockerfile') or 
            self._file_exists(project_path, 'docker-compose.yml') or
            self._file_exists(project_path, 'docker-compose.yaml')):
            structure['dockerized'] = True
        
        return structure
    
    def _assess_complexity(self, project_info: Dict[str, Any]) -> str:
        score = 0
        
        if len(project_info.get('dependencies', [])) > 50:
            score += 2
        elif len(project_info.get('dependencies', [])) > 20:
            score += 1
        
        structure = project_info.get('structure', {})
        if structure.get('monorepo'):
            score += 2
        if structure.get('microservices'):
            score += 2
        
        if not project_info.get('testing'):
            score += 1
        
        if score >= 5:
            return 'high'
        elif score >= 3:
            return 'medium'
        else:
            return 'low'
    
    def _detect_testing(self, project_path: str, language: str) -> bool:
        test_patterns = {
            'javascript': ['**/*.test.js', '**/*.spec.js', '**/tests/**', '**/__tests__/**'],
            'python': ['**/*_test.py', '**/test_*.py', '**/tests/**'],
            'java': ['**/*Test.java', '**/test/**'],
            'go': ['**/*_test.go', '**/test/**'],
            'csharp': ['**/*Test.cs', '**/Tests/**']
        }
        
        patterns = test_patterns.get(language, test_patterns['javascript'])
        
        for pattern in patterns:
            if self._file_exists(project_path, pattern):
                return True
        
        return False
    
    def _detect_build_tools(self, project_path: str, project_info: Dict[str, Any]) -> List[str]:
        tools = []
        
        if self._file_exists(project_path, 'webpack.config.js'):
            tools.append('webpack')
        
        if self._file_exists(project_path, 'vite.config.js'):
            tools.append('vite')
        
        if self._file_exists(project_path, 'Dockerfile'):
            tools.append('docker')
        
        return tools
    
    def _detect_deployment(self, project_path: str, project_info: Dict[str, Any]) -> List[str]:
        strategies = []
        
        if self._file_exists(project_path, 'Dockerfile'):
            strategies.append('docker')
        
        if (self._file_exists(project_path, 'k8s') or 
            self._file_exists(project_path, 'kubernetes')):
            strategies.append('kubernetes')
        
        return strategies
    
    def _read_package_json(self, project_path: str) -> Optional[Dict]:
        try:
            with open(os.path.join(project_path, 'package.json'), 'r') as f:
                return json.load(f)
        except:
            return None
    
    def _read_requirements_txt(self, project_path: str) -> Optional[List[str]]:
        try:
            with open(os.path.join(project_path, 'requirements.txt'), 'r') as f:
                return [line.strip() for line in f if line.strip() and not line.startswith('#')]
        except:
            return None
    
    def _read_pom_xml(self, project_path: str) -> Optional[str]:
        try:
            with open(os.path.join(project_path, 'pom.xml'), 'r') as f:
                return f.read()
        except:
            return None
    
    def _read_go_mod(self, project_path: str) -> Optional[str]:
        try:
            with open(os.path.join(project_path, 'go.mod'), 'r') as f:
                return f.read()
        except:
            return None
    
    def _read_composer_json(self, project_path: str) -> Optional[Dict]:
        try:
            with open(os.path.join(project_path, 'composer.json'), 'r') as f:
                return json.load(f)
        except:
            return None
    
    def _read_csproj(self, project_path: str) -> Optional[str]:
        try:
            csproj_files = list(Path(project_path).glob('*.csproj'))
            if csproj_files:
                with open(csproj_files[0], 'r') as f:
                    return f.read()
        except:
            pass
        return None
    
    def _file_exists(self, project_path: str, pattern: str) -> bool:
        try:
            return len(list(Path(project_path).glob(pattern))) > 0
        except:
            return False
    
    def _detect_python_framework(self, project_path: str) -> str:
        if self._file_exists(project_path, 'manage.py'):
            return 'django'
        elif self._file_exists(project_path, 'app.py'):
            return 'flask'
        elif self._file_exists(project_path, 'main.py'):
            return 'fastapi'
        
        try:
            with open(os.path.join(project_path, 'pyproject.toml'), 'r') as f:
                pyproject_content = f.read()
            if 'django' in pyproject_content.lower() or 'name = "Django"' in pyproject_content:
                return 'django'
            if 'flask' in pyproject_content.lower():
                return 'flask'
            if 'fastapi' in pyproject_content.lower():
                return 'fastapi'
        except:
            pass
            
        return 'unknown'
    
    def _detect_java_framework(self, project_path: str) -> str:
        if self._file_exists(project_path, 'src/main/java/**/Application.java'):
            return 'spring-boot'
        
        try:
            with open(os.path.join(project_path, 'build.gradle'), 'r') as f:
                gradle_content = f.read()
            if 'spring-boot' in gradle_content.lower() or 'springframework' in gradle_content.lower():
                return 'spring-boot'
        except:
            pass
            
        return 'unknown'
    
    def _detect_go_framework(self, project_path: str) -> str:
        go_mod = self._read_go_mod(project_path)
        if go_mod:
            if 'gin-gonic/gin' in go_mod:
                return 'gin'
            elif 'labstack/echo' in go_mod:
                return 'echo'
            elif 'gofiber/fiber' in go_mod:
                return 'fiber'
        return 'unknown'
    
    def _detect_csharp_framework(self, project_path: str) -> str:
        if self._file_exists(project_path, 'Startup.cs'):
            return 'aspnet-core'
        return 'unknown'
    
    def _detect_php_framework(self, project_path: str) -> str:
        if self._file_exists(project_path, 'artisan'):
            return 'laravel'
        elif self._file_exists(project_path, 'composer.json'):
            composer_json = self._read_composer_json(project_path)
            if composer_json and 'symfony/symfony' in composer_json.get('require', {}):
                return 'symfony'
        return 'unknown'


class PipelineGenerator:
    
    def __init__(self):
        self.templates = {
            'github-actions': self._generate_github_actions,
            'gitlab-ci': self._generate_gitlab_ci,
            'jenkins': self._generate_jenkins
        }
    
    def generate(self, project_info: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        platform = config.get('platform', 'github-actions')
        template = self.templates.get(platform)
        
        if not template:
            raise ValueError(f"Неподдерживаемая платформа: {platform}")
        
        pipeline = template(project_info, config)
        output_path = self._save_pipeline(pipeline, project_info, config)
        
        return {
            **pipeline,
            'output_file': output_path,
            'platform': platform
        }
    
    def _generate_github_actions(self, project_info: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        workflow = {
            'name': f"{project_info.get('framework', project_info.get('language', 'Unknown'))} CI/CD",
            'on': {
                'push': {
                    'branches': ['main', 'master', 'develop']
                },
                'pull_request': {
                    'branches': ['main', 'master']
                }
            },
            'jobs': {}
        }
        
        workflow['jobs']['build'] = {
            'runs-on': 'ubuntu-latest',
            'steps': self._generate_build_steps(project_info, config)
        }
        
        if config.get('deployment', {}).get('enabled'):
            workflow['jobs']['deploy'] = {
                'runs-on': 'ubuntu-latest',
                'needs': 'build',
                'if': "github.ref == 'refs/heads/main' && github.event_name == 'push'",
                'steps': self._generate_deploy_steps(project_info, config)
            }
        
        return {
            'content': yaml.dump(workflow, default_flow_style=False, allow_unicode=True),
            'format': 'yaml',
            'filename': '.github/workflows/ci.yml'
        }
    
    def _generate_gitlab_ci(self, project_info: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        pipeline = {
            'stages': ['build', 'test', 'deploy'],
            'variables': self._get_gitlab_variables(project_info, config)
        }
        
        pipeline['build'] = self._generate_gitlab_job('build', project_info, config)
        pipeline['test'] = self._generate_gitlab_job('test', project_info, config)
        
        if config.get('deployment', {}).get('enabled'):
            pipeline['deploy'] = self._generate_gitlab_job('deploy', project_info, config)
        
        return {
            'content': yaml.dump(pipeline, default_flow_style=False, allow_unicode=True),
            'format': 'yaml',
            'filename': '.gitlab-ci.yml'
        }
    
    def _generate_jenkins(self, project_info: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        pipeline = {
            'pipeline': {
                'agent': 'any',
                'stages': self._generate_jenkins_stages(project_info, config),
                'post': self._get_jenkins_post_actions(project_info, config)
            }
        }
        
        return {
            'content': yaml.dump(pipeline, default_flow_style=False, allow_unicode=True),
            'format': 'yaml',
            'filename': 'Jenkinsfile'
        }
    
    def _generate_build_steps(self, project_info: Dict[str, Any], config: Dict[str, Any]) -> List[Dict[str, Any]]:
        steps = []
        
        steps.append({
            'name': 'Checkout',
            'uses': 'actions/checkout@v4'
        })
        
        steps.extend(self._get_language_setup_steps(project_info))
        steps.extend(self._get_dependency_install_steps(project_info))
        
        if project_info.get('testing'):
            steps.extend(self._get_test_steps(project_info))
        
        steps.extend(self._get_build_steps(project_info))
        
        if project_info.get('structure', {}).get('dockerized'):
            steps.extend(self._get_docker_build_steps(project_info))
        
        return steps
    
    def _generate_deploy_steps(self, project_info: Dict[str, Any], config: Dict[str, Any]) -> List[Dict[str, Any]]:
        steps = []
        
        if config.get('deployment', {}).get('strategy') == 'docker':
            steps.extend(self._get_docker_deploy_steps(project_info, config))
        elif config.get('deployment', {}).get('strategy') == 'kubernetes':
            steps.extend(self._get_kubernetes_deploy_steps(project_info, config))
        
        return steps
    
    def _get_language_setup_steps(self, project_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        steps = []
        
        language = project_info.get('language')
        
        if language == 'javascript':
            steps.append({
                'name': 'Setup Node.js',
                'uses': 'actions/setup-node@v4',
                'with': {
                    'node-version': '18',
                    'cache': 'npm'
                }
            })
        elif language == 'python':
            steps.append({
                'name': 'Setup Python',
                'uses': 'actions/setup-python@v4',
                'with': {
                    'python-version': '3.9'
                }
            })
        elif language == 'typescript':
            steps.append({
                'name': 'Setup Node.js',
                'uses': 'actions/setup-node@v4',
                'with': {
                    'node-version': '18',
                    'cache': 'npm'
                }
            })
        elif language == 'c':
            steps.append({
                'name': 'Setup C environment',
                'run': 'sudo apt-get update && sudo apt-get install -y build-essential gcc make'
            })
        elif language == 'java':
            steps.append({
                'name': 'Setup Java',
                'uses': 'actions/setup-java@v3',
                'with': {
                    'java-version': '17',
                    'distribution': 'temurin'
                }
            })
        elif language == 'go':
            steps.append({
                'name': 'Setup Go',
                'uses': 'actions/setup-go@v4',
                'with': {
                    'go-version': '1.21'
                }
            })
        elif language == 'csharp':
            steps.append({
                'name': 'Setup .NET',
                'uses': 'actions/setup-dotnet@v3',
                'with': {
                    'dotnet-version': '6.0'
                }
            })
        
        return steps
    
    def _get_dependency_install_steps(self, project_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        steps = []
        
        language = project_info.get('language')
        
        if language in ['javascript', 'typescript']:
            steps.append({
                'name': 'Install dependencies',
                'run': 'npm ci'
            })
        elif language == 'python':
            steps.append({
                'name': 'Install dependencies',
                'run': 'pip install -r requirements.txt'
            })
        elif language == 'java':
            steps.append({
                'name': 'Install dependencies',
                'run': 'mvn dependency:resolve'
            })
        elif language == 'go':
            steps.append({
                'name': 'Install dependencies',
                'run': 'go mod download'
            })
        elif language == 'csharp':
            steps.append({
                'name': 'Install dependencies',
                'run': 'dotnet restore'
            })
        
        return steps
    
    def _get_test_steps(self, project_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        steps = []
        
        language = project_info.get('language')
        
        if language in ['javascript', 'typescript']:
            steps.append({
                'name': 'Run tests',
                'run': 'npm test'
            })
        elif language == 'python':
            steps.append({
                'name': 'Run tests',
                'run': 'python -m pytest'
            })
        elif language == 'java':
            steps.append({
                'name': 'Run tests',
                'run': 'mvn test'
            })
        elif language == 'go':
            steps.append({
                'name': 'Run tests',
                'run': 'go test ./...'
            })
        elif language == 'csharp':
            steps.append({
                'name': 'Run tests',
                'run': 'dotnet test'
            })
        
        return steps
    
    def _get_build_steps(self, project_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        steps = []
        
        language = project_info.get('language')
        framework = project_info.get('framework')
        
        if language in ['javascript', 'typescript']:
            if framework in ['react', 'vue', 'typescript']:
                steps.append({
                    'name': 'Build',
                    'run': 'npm run build'
                })
        elif language == 'java':
            steps.append({
                'name': 'Build',
                'run': 'mvn package'
            })
        elif language == 'go':
            steps.append({
                'name': 'Build',
                'run': 'go build -o app ./...'
            })
        elif language == 'csharp':
            steps.append({
                'name': 'Build',
                'run': 'dotnet build'
            })
        elif language == 'c':
            steps.append({
                'name': 'Build',
                'run': 'make || gcc -o app *.c || echo "No standard build found"'
            })
        
        return steps
    
    def _get_docker_build_steps(self, project_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        steps = []
        
        steps.append({
            'name': 'Build Docker image',
            'run': 'docker build -t myapp:${{ github.sha }} .'
        })
        
        steps.append({
            'name': 'Test Docker image',
            'run': 'docker run --rm myapp:${{ github.sha }} --version || echo "No version flag"'
        })
        
        return steps
    
    def _get_docker_deploy_steps(self, project_info: Dict[str, Any], config: Dict[str, Any]) -> List[Dict[str, Any]]:
        steps = []
        
        image_name = config.get('deployment', {}).get('imageName', 'myapp')
        
        steps.append({
            'name': 'Build Docker image',
            'run': f'docker build -t {image_name}:${{{{ github.sha }}}} .'
        })
        
        steps.append({
            'name': 'Push to registry',
            'run': f'docker push {image_name}:${{{{ github.sha }}}}'
        })
        
        return steps
    
    def _get_kubernetes_deploy_steps(self, project_info: Dict[str, Any], config: Dict[str, Any]) -> List[Dict[str, Any]]:
        steps = []
        
        steps.append({
            'name': 'Deploy to Kubernetes',
            'run': 'kubectl apply -f k8s/'
        })
        
        return steps
    
    def _get_gitlab_variables(self, project_info: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, str]:
        return {
            'NODE_VERSION': '18',
            'PYTHON_VERSION': '3.9',
            'JAVA_VERSION': '17'
        }
    
    def _generate_gitlab_job(self, stage: str, project_info: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'stage': stage,
            'script': self._get_gitlab_script(stage, project_info),
            'image': self._get_gitlab_image(project_info)
        }
    
    def _get_gitlab_script(self, stage: str, project_info: Dict[str, Any]) -> List[str]:
        language = project_info.get('language')
        
        if stage == 'build':
            if language == 'javascript':
                return ['npm ci', 'npm run build']
            elif language == 'python':
                return ['pip install -r requirements.txt']
            elif language == 'java':
                return ['mvn clean package']
            elif language == 'go':
                return ['go mod download', 'go build ./...']
            elif language == 'csharp':
                return ['dotnet restore', 'dotnet build']
        elif stage == 'test':
            if language == 'javascript':
                return ['npm test']
            elif language == 'python':
                return ['python -m pytest']
            elif language == 'java':
                return ['mvn test']
            elif language == 'go':
                return ['go test ./...']
            elif language == 'csharp':
                return ['dotnet test']
        elif stage == 'deploy':
            return ['echo "Deploy script would go here"']
        
        return ['echo "Unknown stage"']
    
    def _get_gitlab_image(self, project_info: Dict[str, Any]) -> str:
        language = project_info.get('language')
        
        images = {
            'javascript': 'node:18',
            'python': 'python:3.9',
            'java': 'openjdk:17',
            'go': 'golang:1.21',
            'csharp': 'mcr.microsoft.com/dotnet/sdk:6.0'
        }
        
        return images.get(language, 'ubuntu:latest')
    
    def _generate_jenkins_stages(self, project_info: Dict[str, Any], config: Dict[str, Any]) -> List[Dict[str, Any]]:
        return [
            {
                'stage': 'Build',
                'steps': [
                    {'sh': 'echo "Build step"'}
                ]
            },
            {
                'stage': 'Test',
                'steps': [
                    {'sh': 'echo "Test step"'}
                ]
            }
        ]
    
    def _get_jenkins_post_actions(self, project_info: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'always': [
                {'publishTestResults': {'testResultsPattern': '**/test-results.xml'}}
            ]
        }
    
    def _save_pipeline(self, pipeline: Dict[str, Any], project_info: Dict[str, Any], config: Dict[str, Any]) -> str:
        output_dir = config.get('output_dir', project_info.get('path', '.'))
        if not output_dir:
            output_dir = '.'
        output_path = os.path.join(output_dir, pipeline['filename'])
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w') as f:
            f.write(pipeline['content'])
        
        return output_path


class AmazingAutomata:
    
    def __init__(self, options: Dict[str, Any] = None):
        self.detector = ProjectDetector()
        self.generator = PipelineGenerator()
        self.config = options or {}
    
    def analyze_project(self, project_path: str) -> Dict[str, Any]:
        print("🔍 Анализируем проект...")
        
        try:
            project_info = self.detector.detect(project_path)
            
            print("✅ Анализ завершен:")
            print(f"   Язык: {project_info['language']}")
            print(f"   Фреймворк: {project_info['framework'] or 'Не определен'}")
            print(f"   Тип проекта: {project_info['type']}")
            print(f"   Структура: {project_info['structure']}")
            
            return project_info
        except Exception as error:
            print(f"❌ Ошибка при анализе проекта: {error}")
            raise error
    
    def generate_pipeline(self, project_path: str, project_info: Dict[str, Any]) -> Dict[str, Any]:
        print("🚀 Генерируем пайплайн...")
        
        try:
            pipeline = self.generator.generate(project_info, self.config)
            
            print("✅ Пайплайн сгенерирован:")
            print(f"   Платформа: {pipeline['platform']}")
            print(f"   Файл: {pipeline['output_file']}")
            
            return pipeline
        except Exception as error:
            print(f"❌ Ошибка при генерации пайплайна: {error}")
            raise error
    
    def process_project(self, project_path: str) -> Dict[str, Any]:
        print("🎯 Amazing Automata - Универсальный генератор пайплайнов")
        print("=" * 50)
        
        try:
            project_info = self.analyze_project(project_path)
            pipeline = self.generate_pipeline(project_path, project_info)
            
            result = {
                'project_info': project_info,
                'pipeline': pipeline,
                'timestamp': str(pd.Timestamp.now()),
                'success': True
            }
            
            print("\n🎉 Процесс завершен успешно!")
            return result
            
        except Exception as error:
            print(f"\n💥 Процесс завершен с ошибкой: {error}")
            
            return {
                'error': str(error),
                'timestamp': str(pd.Timestamp.now()),
                'success': False
            }
    
    def get_refactoring_recommendations(self, project_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        recommendations = []
        
        if project_info.get('complexity') == 'high':
            recommendations.append({
                'type': 'complexity',
                'message': 'Проект имеет высокую сложность. Рекомендуется разбить на микросервисы.',
                'priority': 'high'
            })
        
        if len(project_info.get('dependencies', [])) > 100:
            recommendations.append({
                'type': 'dependencies',
                'message': 'Большое количество зависимостей. Рассмотрите возможность оптимизации.',
                'priority': 'medium'
            })
        
        if not project_info.get('testing'):
            recommendations.append({
                'type': 'testing',
                'message': 'Не обнаружены тесты. Рекомендуется добавить тестирование.',
                'priority': 'high'
            })
        
        return recommendations


def main():
    parser = argparse.ArgumentParser(description='Amazing Automata - Universal CI/CD Pipeline Generator')
    parser.add_argument('command', choices=['analyze', 'generate', 'help'], help='Команда для выполнения')
    parser.add_argument('path', nargs='?', help='Путь к проекту')
    parser.add_argument('--platform', default='github-actions', help='Платформа CI/CD')
    parser.add_argument('--output', help='Директория для сохранения')
    parser.add_argument('--deploy', action='store_true', help='Включить деплой')
    parser.add_argument('--no-security', action='store_true', help='Отключить проверки безопасности')
    parser.add_argument('--no-tests', action='store_true', help='Отключить тесты')
    parser.add_argument('--verbose', action='store_true', help='Подробный вывод')
    
    args = parser.parse_args()
    
    if args.command == 'help':
        print("🎯 Amazing Automata - Универсальный генератор CI/CD пайплайнов")
        print("=" * 60)
        print()
        print("Основные команды:")
        print("  analyze <path>     - Анализирует проект")
        print("  generate <path>    - Генерирует пайплайн")
        print("  help              - Показывает справку")
        print()
        print("Примеры использования:")
        print("  python amazing_automata.py analyze ./my-project")
        print("  python amazing_automata.py generate ./my-project --platform github-actions")
        return
    
    if not args.path:
        print("❌ Ошибка: Не указан путь к проекту")
        sys.exit(1)
    
    config = {
        'platform': args.platform,
        'output_dir': args.output,
        'deployment': {'enabled': args.deploy},
        'security': {'enabled': not args.no_security},
        'testing': {'enabled': not args.no_tests}
    }
    
    automata = AmazingAutomata(config)
    
    try:
        if args.command == 'analyze':
            project_info = automata.analyze_project(args.path)
            if args.verbose:
                print("\n📊 Подробная информация:")
                print(json.dumps(project_info, indent=2, ensure_ascii=False))
        
        elif args.command == 'generate':
            result = automata.process_project(args.path)
            
            if result['success']:
                recommendations = automata.get_refactoring_recommendations(result['project_info'])
                if recommendations:
                    print("\n💡 Рекомендации по рефакторингу:")
                    for i, rec in enumerate(recommendations, 1):
                        print(f"   {i}. {rec['message']} ({rec['priority']})")
            else:
                print(f"\n💥 Ошибка при генерации: {result['error']}")
                sys.exit(1)
    
    except Exception as error:
        print(f"❌ Ошибка: {error}")
        sys.exit(1)


if __name__ == '__main__':
    import pandas as pd
    main()
